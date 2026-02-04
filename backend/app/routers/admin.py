"""
Admin routes - Separate routes for C-Admin and CM-Admin
Refactored to use Users with specific roles via `require_roles` dependency.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Complaint, User, ComplaintMessage, ComplaintStatusHistory, ComplaintStatus, Department
from app.deps import require_roles
from app.schemas import ComplaintUpdate, AdminComplaintResponse, ComplaintMessageCreate, ComplaintMessageResponse

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# === COMMON STATS ENDPOINT ===
@router.get("/stats")
def get_admin_stats(current_admin: User = Depends(require_roles("c_admin", "cm_admin")), db: Session = Depends(get_db)):
    """Get complaint statistics"""
    total = db.query(Complaint).count()
    pending = db.query(Complaint).filter(Complaint.status == ComplaintStatus.pending).count()
    in_progress = db.query(Complaint).filter(Complaint.status == ComplaintStatus.in_progress).count()
    solved = db.query(Complaint).filter(Complaint.status == ComplaintStatus.solved).count()

    # Count complaints updated by THIS specific admin
    updated_by_me = db.query(Complaint).filter(Complaint.updated_by_admin == current_admin.email).count()

    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "solved": solved,
        "updated_by_me": updated_by_me
    }

# === C-ADMIN ROUTES ===
@router.get("/c-admin/complaints", response_model=List[AdminComplaintResponse])
def get_complaints_for_c_admin(
    admin: User = Depends(require_roles("c_admin")),
    db: Session = Depends(get_db)
):
    """Get all complaints for C-Admin to manage"""
    complaints = db.query(Complaint).join(User).all()

    result = []
    for complaint in complaints:
        complaint_dict = {
            "id": complaint.id,
            "user_id": complaint.user_id,
            "department": complaint.department,
            "district": getattr(complaint, 'district', None),
            "subcategory": getattr(complaint, 'subcategory', None),
            "title": complaint.title,
            "description": complaint.description,
            "location": complaint.location,
            "status": complaint.status.name if hasattr(complaint.status, 'name') else complaint.status,
            "admin_response": complaint.admin_response,
            "image_url": complaint.image_path if hasattr(complaint, 'image_path') else None,
            "voice_url": complaint.voice_path if hasattr(complaint, 'voice_path') else None,
            "created_at": complaint.created_at,
            "updated_at": complaint.updated_at,
            "user_name": complaint.user.name if complaint.user else "Deleted User",
            "user_email": complaint.user.email if complaint.user else "N/A",
            "user_phone": complaint.user.phone if complaint.user else "N/A",
            "user_profile_picture": complaint.user.profile_picture if complaint.user else None
        }
        result.append(complaint_dict)

    return result

@router.put("/c-admin/complaints/{complaint_id}")
def update_complaint_by_c_admin(
    complaint_id: int,
    update_data: ComplaintUpdate,
    admin: User = Depends(require_roles("c_admin")),
    db: Session = Depends(get_db)
):
    """C-Admin can update to pending or in_progress only"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    # C-Admin can only set pending or in_progress
    if update_data.status and update_data.status not in ["pending", "in_progress"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="C-Admin can only mark complaints as 'pending' or 'in_progress'"
        )

    if update_data.status:
        complaint.status = update_data.status  # type: ignore
        complaint.updated_by_admin = admin.email  # type: ignore

    if update_data.admin_response:
        complaint.admin_response = update_data.admin_response  # type: ignore

    db.commit()
    db.refresh(complaint)

    return {"message": "Complaint updated successfully", "status": complaint.status}

# === CM-ADMIN ROUTES ===
@router.get("/cm-admin/stats")
def get_cm_admin_stats(
    admin: User = Depends(require_roles("cm_admin")),
    db: Session = Depends(get_db)
):
    """Get statistics for CM-Admin dashboard (restricted to admin's department)"""
    if not admin.department_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CM-Admin has no department assigned")

    total = db.query(Complaint).filter(Complaint.department_id == admin.department_id).count()
    pending = db.query(Complaint).filter(Complaint.department_id == admin.department_id, Complaint.status == ComplaintStatus.pending).count()
    in_progress = db.query(Complaint).filter(Complaint.department_id == admin.department_id, Complaint.status == ComplaintStatus.in_progress).count()

    # Count complaints updated (solved) by THIS CM-Admin within their department
    solved_by_me = db.query(Complaint).filter(
        Complaint.department_id == admin.department_id,
        Complaint.status == ComplaintStatus.solved,
        Complaint.updated_by_admin == admin.email
    ).count()

    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "solved": solved_by_me,
        "updated_by_me": solved_by_me
    }

@router.get("/cm-admin/complaints", response_model=List[AdminComplaintResponse])
def get_complaints_for_cm_admin(
    admin: User = Depends(require_roles("cm_admin")),
    db: Session = Depends(get_db)
):
    """Get complaints that CM-Admin can resolve (restricted to their department)"""
    if not admin.department_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CM-Admin has no department assigned")

    complaints = db.query(Complaint).filter(Complaint.department_id == admin.department_id).join(User).all()

    result = []
    for complaint in complaints:
        complaint_dict = {
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
            "user_name": complaint.user.name if complaint.user else "Deleted User",
            "user_email": complaint.user.email if complaint.user else "N/A",
            "user_phone": complaint.user.phone if complaint.user else "N/A",
            "user_profile_picture": complaint.user.profile_picture if complaint.user else None
        }
        result.append(complaint_dict)

    return result

@router.put("/cm-admin/complaints/{complaint_id}")
def update_complaint_by_cm_admin(
    complaint_id: int,
    update_data: ComplaintUpdate,
    admin: User = Depends(require_roles("cm_admin")),
    db: Session = Depends(get_db)
):
    """CM-Admin can add responses/comments to complaints in their department.

    CM-Admin cannot mark complaints as 'solved' via this endpoint.
    Use the dedicated endpoint to set status to 'in_progress'.
    """
    if not admin.department_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CM-Admin has no department assigned")

    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    if complaint.department_id != admin.department_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: not your department")

    if update_data.status:
        # CM-Admin not allowed to set 'solved' status here
        if update_data.status == "solved":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CM-Admin cannot mark complaints as 'solved'")
        # Only allow in_progress via dedicated endpoint
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Use the 'in-progress' endpoint to change status")

    if update_data.admin_response:
        # Append CM-Admin response
        note = f"[CM-Admin]: {update_data.admin_response}"
        if complaint.admin_response:
            complaint.admin_response = f"{complaint.admin_response}\n\n{note}"  # type: ignore
        else:
            complaint.admin_response = note  # type: ignore
        complaint.updated_by_admin = admin.email  # type: ignore

    db.commit()
    db.refresh(complaint)

    return {"message": "Complaint updated successfully", "status": complaint.status.value if hasattr(complaint.status, 'value') else str(complaint.status)}


@router.put("/cm-admin/complaints/{complaint_id}/in-progress")
def mark_complaint_in_progress(
    complaint_id: int,
    admin: User = Depends(require_roles("cm_admin")),
    db: Session = Depends(get_db)
):
    """Mark a complaint as 'in_progress' for the CM-Admin's department only"""
    if not admin.department_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CM-Admin has no department assigned")

    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    if complaint.department_id != admin.department_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: not your department")

    # Only allow moving to in_progress (cannot mark solved)
    if complaint.status == ComplaintStatus.solved:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change status of solved complaints")

    old_status = complaint.status
    setattr(complaint, 'status', ComplaintStatus.in_progress)
    complaint.updated_by_admin = admin.email  # type: ignore

    # Add status history
    history = ComplaintStatusHistory(
        complaint_id=complaint.id,
        old_status=old_status,
        new_status=complaint.status,
        changed_by=admin.id,
        note="Marked in-progress by CM-Admin"
    )
    db.add(history)

    db.commit()
    db.refresh(complaint)

    return {"message": "Complaint marked in_progress", "status": complaint.status.value if hasattr(complaint.status, 'value') else str(complaint.status)}


@router.post("/cm-admin/complaints/{complaint_id}/messages", response_model=ComplaintMessageResponse)
def add_message_to_complaint(
    complaint_id: int,
    payload: ComplaintMessageCreate,
    admin: User = Depends(require_roles("cm_admin")),
    db: Session = Depends(get_db)
):
    """Add a message/comment to a complaint within the CM-Admin's department"""
    if not admin.department_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CM-Admin has no department assigned")

    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    if complaint.department_id != admin.department_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: not your department")

    message = ComplaintMessage(
        complaint_id=complaint.id,
        sender_id=admin.id,
        message=payload.message
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    return {
        "id": message.id,
        "complaint_id": message.complaint_id,
        "sender_id": message.sender_id,
        "message": message.message,
        "created_at": message.created_at,
        "sender_name": admin.name
    }


# === C-ADMIN (Central Admin) ROUTES ===
@router.get("/c-admin/complaints/{complaint_id}/messages", response_model=List[ComplaintMessageResponse])
def get_messages_for_complaint(
    complaint_id: int,
    admin: User = Depends(require_roles("c_admin")),
    db: Session = Depends(get_db),
    sender_role: Optional[str] = None
):
    """Get all messages for a complaint. Optionally filter by sender_role (e.g., 'cm_admin')"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    messages = db.query(ComplaintMessage).filter(ComplaintMessage.complaint_id == complaint_id).order_by(ComplaintMessage.created_at.asc()).all()

    # Optional filter by sender role
    if sender_role:
        filtered = []
        for m in messages:
            if m.sender and m.sender.role and m.sender.role.name == sender_role:
                filtered.append(m)
        messages = filtered

    result = []
    for m in messages:
        result.append({
            "id": m.id,
            "complaint_id": m.complaint_id,
            "sender_id": m.sender_id,
            "message": m.message,
            "created_at": m.created_at,
            "sender_name": m.sender.name if m.sender else None
        })

    return result


@router.put("/c-admin/complaints/{complaint_id}/solve")
def mark_complaint_solved(
    complaint_id: int,
    admin: User = Depends(require_roles("c_admin")),
    db: Session = Depends(get_db),
    admin_response: Optional[str] = None
):
    """Mark a complaint as 'solved'. This action is global and requires c_admin role."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    # If already solved, no-op with 400
    if complaint.status == ComplaintStatus.solved:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Complaint already solved")

    old_status = complaint.status
    setattr(complaint, 'status', ComplaintStatus.solved)
    complaint.updated_by_admin = admin.email  # type: ignore

    # Append c-admin response if provided
    if admin_response:
        note = f"[C-Admin]: {admin_response}"
        if complaint.admin_response:
            setattr(complaint, 'admin_response', f"{complaint.admin_response}\n\n{note}")
        else:
            setattr(complaint, 'admin_response', note)

    # Add status history entry
    history = ComplaintStatusHistory(
        complaint_id=complaint.id,
        old_status=old_status,
        new_status=complaint.status,
        changed_by=admin.id,
        note="Marked solved by C-Admin"
    )
    db.add(history)

    db.commit()
    db.refresh(complaint)

    return {"message": "Complaint marked as solved", "status": complaint.status.value if hasattr(complaint.status, 'value') else str(complaint.status)}