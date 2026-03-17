# routers/complaints.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header, Form
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import Complaint, User
from schemas import ComplaintResponse, StatusUpdate
from utils import get_current_user_id, get_current_user_role
import os, uuid
import cloudinary
import cloudinary.uploader

router = APIRouter(prefix="/api/complaints", tags=["Complaints"])

# ✅ Cloudinary config
cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key    = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
)

def upload_to_cloudinary(file, folder):
    """Upload file to Cloudinary and return URL"""
    try:
        result = cloudinary.uploader.upload(
            file.file,
            folder=folder,
            resource_type="auto"
        )
        return result["secure_url"]
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        return None


# ─── RAISE COMPLAINT ──────────────────────────────────────
@router.post("/", response_model=ComplaintResponse)
def create_complaint(
    citizen_name:  str = Form(...),
    age:           int = Form(...),
    district:      str = Form(...),
    department:    str = Form(...),
    subcategory:   str = Form(...),
    description:   str = Form(...),
    voice_file:    Optional[UploadFile] = File(None),
    proof_doc:     Optional[UploadFile] = File(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user_id = get_current_user_id(authorization)

    voice_path = None
    if voice_file and voice_file.filename:
        voice_path = upload_to_cloudinary(voice_file, "voiceoftn/voices")

    proof_path = None
    if proof_doc and proof_doc.filename:
        proof_path = upload_to_cloudinary(proof_doc, "voiceoftn/proofs")

    complaint = Complaint(
        user_id=user_id, citizen_name=citizen_name, age=age,
        district=district, department=department, subcategory=subcategory,
        description=description, voice_file=voice_path,
        proof_doc=proof_path, status="pending"
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


# ─── GET ALL COMPLAINTS ───────────────────────────────────
@router.get("/")
def get_all_complaints(
    department: Optional[str] = None,
    status:     Optional[str] = None,
    district:   Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Complaint)
    if department: query = query.filter(Complaint.department == department)
    if status:     query = query.filter(Complaint.status     == status)
    if district:   query = query.filter(Complaint.district   == district)
    return query.order_by(Complaint.created_at.desc()).all()


# ─── GET MY COMPLAINTS ────────────────────────────────────
@router.get("/my")
def get_my_complaints(authorization: str = Header(None), db: Session = Depends(get_db)):
    user_id = get_current_user_id(authorization)
    return db.query(Complaint).filter(
        Complaint.user_id == user_id
    ).order_by(Complaint.created_at.desc()).all()


# ─── GET ASSIGNED COMPLAINTS (c_admin only) ──────────────
@router.get("/assigned")
def get_assigned_complaints(authorization: str = Header(None), db: Session = Depends(get_db)):
    info = get_current_user_role(authorization)
    if info["role"] != "c_admin":
        raise HTTPException(status_code=403, detail="c_admin only")
    return db.query(Complaint).filter(
        Complaint.assigned_to == info["user_id"]
    ).order_by(Complaint.created_at.desc()).all()


# ─── UPDATE STATUS ────────────────────────────────────────
@router.put("/{complaint_id}/status")
def update_status(
    complaint_id:  int,
    data:          StatusUpdate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    info = get_current_user_role(authorization)
    if info["role"] not in ["c_admin", "cm_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    allowed = {
        "cm_admin": ["under_investigation", "solved"],
        "c_admin":  ["resolved", "rejected"]
    }
    if data.status not in allowed[info["role"]]:
        raise HTTPException(status_code=400, detail=f"Cannot set status to {data.status}")

    complaint.status = data.status
    if data.message:
        complaint.admin_message = data.message

    if info["role"] == "cm_admin" and data.status == "under_investigation":
        if data.assigned_to:
            complaint.assigned_to = data.assigned_to
        else:
            c_admin = db.query(User).filter(
                User.role     == "c_admin",
                User.district == complaint.district
            ).first()
            if c_admin:
                complaint.assigned_to = c_admin.id

    db.commit()
    db.refresh(complaint)
    return complaint


# ─── EDIT COMPLAINT ───────────────────────────────────────
@router.put("/{complaint_id}/edit")
def edit_complaint(
    complaint_id:  int,
    data:          dict,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user_id = get_current_user_id(authorization)
    complaint = db.query(Complaint).filter(
        Complaint.id == complaint_id, Complaint.user_id == user_id
    ).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if complaint.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending complaints can be edited")
    if data.get("description"): complaint.description = data["description"]
    if data.get("subcategory"): complaint.subcategory = data["subcategory"]
    db.commit()
    db.refresh(complaint)
    return complaint


# ─── DELETE COMPLAINT ─────────────────────────────────────
@router.delete("/{complaint_id}")
def delete_complaint(
    complaint_id:  int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user_id = get_current_user_id(authorization)
    complaint = db.query(Complaint).filter(
        Complaint.id == complaint_id, Complaint.user_id == user_id
    ).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if complaint.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending complaints can be deleted")
    db.delete(complaint)
    db.commit()
    return {"message": "Deleted successfully"}


# ─── GET SINGLE COMPLAINT ─────────────────────────────────
@router.get("/{complaint_id}")
def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint