from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas, auth
import shutil
import os

router = APIRouter(prefix="/complaints", tags=["Complaints"])

@router.post("/", response_model=schemas.ComplaintResponse)
def create_complaint(
    title: str = Form(...),
    description: str = Form(...),
    department_id: int = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    filename = None
    if file:
        filename = f"{current_user.id}_{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        with open(f"uploads/{filename}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    new_complaint = models.Complaint(
        title=title,
        description=description,
        department_id=department_id,
        user_id=current_user.id,
        file_path=filename
    )
    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)
    return new_complaint

@router.get("/my", response_model=List[schemas.ComplaintResponse])
def get_my_complaints(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Complaint).filter(models.Complaint.user_id == current_user.id).all()

# Admin endpoints
@router.get("/all", response_model=List[schemas.ComplaintResponse])
def get_all_complaints(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return db.query(models.Complaint).all()

@router.put("/{complaint_id}", response_model=schemas.ComplaintResponse)
def update_complaint_status(
    complaint_id: int,
    update_data: schemas.ComplaintUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    complaint.status = update_data.status
    if update_data.admin_response:
        complaint.admin_response = update_data.admin_response
        
    db.commit()
    db.refresh(complaint)
    return complaint

@router.get("/public", response_model=List[schemas.ComplaintResponse])
def get_public_complaints(db: Session = Depends(get_db)):
    # This can be used for the home page scroll
    return db.query(models.Complaint).order_by(models.Complaint.id.desc()).limit(10).all()