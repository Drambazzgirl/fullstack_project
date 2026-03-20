# routers/auth.py - All citizen authentication routes

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserRegister, UserUpdate, UserResponse, Token
from utils import hash_password, verify_password, create_token, get_current_user_id
import os
import cloudinary
import cloudinary.uploader

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# ✅ Cloudinary config
cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key    = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
)


# ─── REGISTER ─────────────────────────────────────────────
@router.post("/register")
def register(data: UserRegister, db: Session = Depends(get_db)):
    email = data.email.lower().strip()
    
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name          = data.name,
        email         = email,
        phone         = data.phone,
        password_hash = hash_password(data.password),
        role          = "citizen"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Registration successful", "user_id": new_user.id}


# ─── LOGIN (JSON format) ───────────────────────────────────
@router.post("/login/json", response_model=Token)
def login_json(data: dict, db: Session = Depends(get_db)):
    email    = (data.get("username") or data.get("email") or "").lower().strip()
    password = data.get("password")

    user = db.query(User).filter(User.email == email, User.role == "citizen").first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token({"user_id": user.id, "role": user.role, "email": user.email})
    return Token(
        access_token = token,
        token_type   = "bearer",
        role         = user.role,
        email        = user.email,
        name         = user.name
    )


# ─── GET MY PROFILE ───────────────────────────────────────
@router.get("/me", response_model=UserResponse)
def get_me(authorization: str = Header(None), db: Session = Depends(get_db)):
    user_id = get_current_user_id(authorization)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ─── UPDATE MY PROFILE ────────────────────────────────────
@router.put("/me", response_model=UserResponse)
def update_me(data: UserUpdate, authorization: str = Header(None), db: Session = Depends(get_db)):
    user_id = get_current_user_id(authorization)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.name:     user.name     = data.name
    if data.phone:    user.phone    = data.phone
    if data.district: user.district = data.district
    if data.age:      user.age      = data.age

    db.commit()
    db.refresh(user)
    return user


# ─── UPLOAD PROFILE PICTURE ───────────────────────────────
@router.post("/upload-profile-picture")
def upload_profile_pic(
    file: UploadFile = File(...),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user_id = get_current_user_id(authorization)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Cloudinary-ல் upload பண்ணு
    try:
        result = cloudinary.uploader.upload(
            file.file,
            folder="voiceoftn/profiles",
            resource_type="image"
        )
        user.profile_picture = result["secure_url"]
        db.commit()
        return {"profile_picture": user.profile_picture}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")