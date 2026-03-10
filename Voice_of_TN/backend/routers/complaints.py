# routers/complaints.py - All complaint routes

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header, Form
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import Complaint, User
from schemas import ComplaintCreate, ComplaintResponse, StatusUpdate
from utils import get_current_user_id, get_current_user_role
import os, shutil, uuid


router = APIRouter(prefix="/api/complaints", tags=["Complaints"])

UPLOAD_BASE = "/tmp/uploads" if os.environ.get("VERCEL") else "uploads"
VOICE_DIR = f"{UPLOAD_BASE}/voices"
PROOF_DIR = f"{UPLOAD_BASE}/proofs"
os.makedirs(VOICE_DIR, exist_ok=True)
os.makedirs(PROOF_DIR, exist_ok=True)


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
        ext      = voice_file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(VOICE_DIR, filename)
        with open(filepath, "wb") as f:
            shutil.copyfileobj(voice_file.file, f)
        voice_path = f"/uploads/voices/{filename}"

    proof_path = None
    if proof_doc and proof_doc.filename:
        ext      = proof_doc.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(PROOF_DIR, filename)
        with open(filepath, "wb") as f:
            shutil.copyfileobj(proof_doc.file, f)
        proof_path = f"/uploads/proofs/{filename}"

    complaint = Complaint(
        user_id      = user_id,
        citizen_name = citizen_name,
        age          = age,
        district     = district,
        department   = department,
        subcategory  = subcategory,
        description  = description,
        voice_file   = voice_path,
        proof_doc    = proof_path,
        status       = "pending"
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


# ─── EDIT COMPLAINT (citizen only) ───────────────
@router.put("/{complaint_id}/edit")
def edit_complaint(
    complaint_id:  int,
    data:          dict,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user_id = get_current_user_id(authorization)
    complaint = db.query(Complaint).filter(
        Complaint.id      == complaint_id,
        Complaint.user_id == user_id
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


# ─── GET ALL COMPLAINTS ────────────────────────────────────
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
    complaints = query.order_by(Complaint.created_at.desc()).all()
    return complaints


# ─── GET MY COMPLAINTS ────────────────────────────────────
@router.get("/my")
def get_my_complaints(authorization: str = Header(None), db: Session = Depends(get_db)):
    user_id = get_current_user_id(authorization)
    complaints = db.query(Complaint).filter(
        Complaint.user_id == user_id
    ).order_by(Complaint.created_at.desc()).all()
    return complaints


# ─── UPDATE STATUS ───────────────────────────────────────
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

    db.commit()
    db.refresh(complaint)
    return complaint


# ─── DELETE COMPLAINT (citizen only) ─────────────
@router.delete("/{complaint_id}")
def delete_complaint(
    complaint_id:  int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user_id = get_current_user_id(authorization)
    complaint = db.query(Complaint).filter(
        Complaint.id      == complaint_id,
        Complaint.user_id == user_id
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