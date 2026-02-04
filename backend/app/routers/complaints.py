"""
Complaint routes - handles complaint operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from jose import JWTError, jwt  # type: ignore
from datetime import datetime
import os
import shutil
from pathlib import Path

from app.database import get_db
from app.models import Complaint, User, Department, ComplaintStatus
from app.schemas import ComplaintCreate, ComplaintResponse
from app.deps import get_current_user
from app.config import settings

router = APIRouter(prefix="/api/complaints", tags=["Complaints"])

# ========================================
# Optional OAuth2 Scheme (for public endpoints)
# ========================================

oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="api/auth/login",
    auto_error=False  # Don't raise error if no token provided
)


# ========================================
# Helper Function: Optional Authentication
# ========================================

def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise return None.
    This allows endpoints to be accessed both with and without authentication.
    """
    if not token:
        return None
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        
        if email is None:
            return None
            
    except JWTError:
        return None
    
    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    return user


# ========================================
# CREATE COMPLAINT (Requires Authentication)
# ========================================

@router.post("/", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    department: str = Form(...),
    district: str = Form(...),
    subcategory: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    location: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    voice_recording: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),  # Authentication required
    db: Session = Depends(get_db)
):
    """
    Create a new complaint with optional file uploads.

    Required Authentication: Yes

    Steps:
    1. Get current user from JWT token
    2. Handle file uploads (image and voice)
    3. Resolve Department (create if missing) and create complaint linked to user
    4. Return created complaint
    """
    image_url = None
    voice_url = None

    # ========================================
    # Handle Image Upload
    # ========================================
    if image:
        # Validate file type
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file must be an image (JPG, PNG, etc.)"
            )

        # Validate file size (max 5MB)
        content = await image.read()
        if len(content) > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image size must be less than 5MB"
            )

        # Create uploads directory
        upload_dir = Path("uploads/complaints")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        file_extension = Path(image.filename or "image.jpg").suffix
        timestamp = int(datetime.utcnow().timestamp())
        filename = f"complaint_{current_user.id}_{timestamp}{file_extension}"
        file_path = upload_dir / filename

        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        image_url = f"/uploads/complaints/{filename}"

    # ========================================
    # Handle Voice Recording Upload
    # ========================================
    if voice_recording:
        # Validate file type
        if not voice_recording.content_type or not voice_recording.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file must be an audio file"
            )

        # Create uploads directory
        upload_dir = Path("uploads/voice_recordings")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        file_extension = Path(voice_recording.filename or "recording.wav").suffix
        timestamp = int(datetime.utcnow().timestamp())
        filename = f"voice_{current_user.id}_{timestamp}{file_extension}"
        file_path = upload_dir / filename

        # Save file
        content = await voice_recording.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        voice_url = f"/uploads/voice_recordings/{filename}"

    # ========================================
    # Resolve Department (create if missing) and create complaint
    # ========================================
    dept = db.query(Department).filter(Department.name == department).first()
    if not dept:
        dept = Department(name=department)
        db.add(dept)
        db.commit()
        db.refresh(dept)

    new_complaint = Complaint(
        user_id=current_user.id,
        department_id=dept.id,
        district=district,
        subcategory=subcategory,
        title=title,
        description=description,
        location=location,
        status=ComplaintStatus.pending,
        image_path=image_url,
        voice_path=voice_url
    )

    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)

    # Map DB values to the expected response schema (image_url / voice_url)
    return {
        "id": new_complaint.id,
        "user_id": new_complaint.user_id,
        "department": dept.name,
        "district": new_complaint.district,
        "subcategory": new_complaint.subcategory,
        "title": new_complaint.title,
        "description": new_complaint.description,
        "location": new_complaint.location,
        "status": new_complaint.status.value if hasattr(new_complaint.status, 'value') else str(new_complaint.status),
        "admin_response": new_complaint.admin_response,
        "image_url": new_complaint.image_path,
        "voice_url": new_complaint.voice_path,
        "created_at": new_complaint.created_at,
        "updated_at": new_complaint.updated_at,
        "user_name": current_user.name,
        "user_profile_picture": current_user.profile_picture
    }


# ========================================
# GET ALL COMPLAINTS (Public - No Authentication Required)
# ========================================

@router.get("/", response_model=List[ComplaintResponse])
def get_all_complaints(
    department: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)  # Optional auth
):
    """
    Get all complaints (PUBLIC ENDPOINT - no authentication required).

    Anyone can view all complaints, but filtering options are available.

    Query Parameters:
    - department: Filter by department name (optional)
    - status_filter: Filter by status - pending, in_progress, solved (optional)

    Returns: List of all complaints ordered by most recent first
    """
    # Start with base query
    query = db.query(Complaint).join(Department)

    # Apply filters if provided
    if department:
        query = query.filter(Department.name == department)

    if status_filter:
        try:
            status_enum = ComplaintStatus(status_filter)
            query = query.filter(Complaint.status == status_enum)
        except Exception:
            # fall back to comparing by string value
            query = query.filter(Complaint.status == status_filter)

    # Order by most recent first
    complaints = query.order_by(Complaint.created_at.desc()).all()

    # Populate user info and convert to dict for schema compatibility
    result = []
    for c in complaints:
        complaint_data = {
            "id": c.id,
            "user_id": c.user_id,
            "department": c.department.name if c.department else None,
            "district": c.district,
            "subcategory": c.subcategory,
            "title": c.title,
            "description": c.description,
            "location": c.location,
            "status": c.status.value if hasattr(c.status, 'value') else str(c.status),
            "admin_response": c.admin_response,
            "image_url": c.image_path,
            "voice_url": c.voice_path,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
            "user_name": c.user.name if c.user else "Anonymous",
            "user_profile_picture": c.user.profile_picture if c.user else None
        }
        result.append(complaint_data)
            
    return result

@router.get("/me", response_model=List[ComplaintResponse])
def get_my_complaints(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    complaints = db.query(Complaint).filter(Complaint.user_id == current_user.id).order_by(Complaint.created_at.desc()).all()

    result = []
    for c in complaints:
        complaint_data = {
            "id": c.id,
            "user_id": c.user_id,
            "department": c.department.name if c.department else None,
            "district": c.district,
            "subcategory": c.subcategory,
            "title": c.title,
            "description": c.description,
            "location": c.location,
            "status": c.status.value if hasattr(c.status, 'value') else str(c.status),
            "admin_response": c.admin_response,
            "image_url": c.image_path,
            "voice_url": c.voice_path,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
            "user_name": current_user.name,
            "user_profile_picture": current_user.profile_picture
        }
        result.append(complaint_data)
        
    return result


# ========================================
# GET SPECIFIC COMPLAINT BY ID (Public)
# ========================================

@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)  # Optional auth
):
    """
    Get a specific complaint by ID.

    Public endpoint - anyone can view any complaint details.
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()

    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID {complaint_id} not found"
        )

    return {
        "id": complaint.id,
        "user_id": complaint.user_id,
        "department": complaint.department.name if complaint.department else None,
        "district": complaint.district,
        "subcategory": complaint.subcategory,
        "title": complaint.title,
        "description": complaint.description,
        "location": complaint.location,
        "status": complaint.status.value if hasattr(complaint.status, 'value') else str(complaint.status),
        "admin_response": complaint.admin_response,
        "image_url": complaint.image_path,
        "voice_url": complaint.voice_path,
        "created_at": complaint.created_at,
        "updated_at": complaint.updated_at,
        "user_name": complaint.user.name if complaint.user else "Anonymous",
        "user_profile_picture": complaint.user.profile_picture if complaint.user else None
    }


# ========================================
# UPDATE COMPLAINT (Only Owner or Admin)
# ========================================

@router.put("/{complaint_id}", response_model=ComplaintResponse)
def update_complaint(
    complaint_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user),  # Authentication required
    db: Session = Depends(get_db)
):
    """
    Update a complaint (only the owner can update).

    Required Authentication: Yes
    Permissions: Only complaint owner can update
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()

    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )

    # Check if user is the owner
    if complaint.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own complaints"
        )

    # Only allow updates if status is pending
    if complaint.status != ComplaintStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update complaint after it has been processed"
        )

    # Update fields
    if title:
        complaint.title = title  # type: ignore
    if description:
        complaint.description = description  # type: ignore

    db.commit()
    db.refresh(complaint)

    return {
        "id": complaint.id,
        "user_id": complaint.user_id,
        "department": complaint.department.name if complaint.department else None,
        "district": complaint.district,
        "subcategory": complaint.subcategory,
        "title": complaint.title,
        "description": complaint.description,
        "location": complaint.location,
        "status": complaint.status.value if hasattr(complaint.status, 'value') else str(complaint.status),
        "admin_response": complaint.admin_response,
        "image_url": complaint.image_path,
        "voice_url": complaint.voice_path,
        "created_at": complaint.created_at,
        "updated_at": complaint.updated_at,
        "user_name": current_user.name,
        "user_profile_picture": current_user.profile_picture
    }


# ========================================
# DELETE COMPLAINT (Only Owner)
# ========================================

@router.delete("/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_complaint(
    complaint_id: int,
    current_user: User = Depends(get_current_user),  # Authentication required
    db: Session = Depends(get_db)
):
    """
    Delete a complaint (only the owner can delete).
    
    Required Authentication: Yes
    Permissions: Only complaint owner can delete
    Restriction: Can only delete if status is 'pending'
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    # Check if user is the owner
    if complaint.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own complaints"
        )
    
    # Only allow deletion if status is pending
    if complaint.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete complaint after it has been processed"
        )
    
    # Delete associated files if they exist
    if complaint.image_path:
        image_path = Path(f".{complaint.image_path}")
        if image_path.exists():
            image_path.unlink()
    
    if complaint.voice_path:
        voice_path = Path(f".{complaint.voice_path}")
        if voice_path.exists():
            voice_path.unlink()
    
    # Delete complaint from database
    db.delete(complaint)
    db.commit()
    
    return None