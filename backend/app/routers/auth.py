"""
Authentication routes - handles user and admin registration/login
Refactored to use centralized security helpers and role-based Users.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Role, Department
from app.schemas import UserCreate, UserLogin, UserResponse, UserUpdate, Token, AdminRegister
from app.config import settings
from app.security import get_password_hash, verify_password, create_access_token
from app.deps import get_current_user
from pathlib import Path
from datetime import datetime
import os

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Utility to get or create a role by name
def _get_or_create_role(db: Session, role_name: str) -> Role:
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        role = Role(name=role_name)
        db.add(role)
        db.commit()
        db.refresh(role)
    return role

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user_role = _get_or_create_role(db, "user")

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password=get_password_hash(user_data.password),
        role_id=user_role.id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/register/admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_admin(admin_data: AdminRegister, db: Session = Depends(get_db)):
    # Protect admin creation with a registration secret
    secret = settings.ADMIN_REGISTRATION_SECRET
    if secret and admin_data.registration_secret != secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin registration secret")

    if admin_data.admin_type not in ("c_admin", "cm_admin"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid admin_type")

    if db.query(User).filter(User.email == admin_data.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    role = _get_or_create_role(db, admin_data.admin_type)

    # if cm_admin, department_id is required
    dept_id = None
    if admin_data.admin_type == "cm_admin":
        if not admin_data.department_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="department_id is required for cm_admin")
        dept = db.query(Department).filter(Department.id == admin_data.department_id).first()
        if not dept:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid department_id")
        dept_id = dept.id

    new_admin = User(
        name=admin_data.name,
        email=admin_data.email,
        password=get_password_hash(admin_data.password),
        role_id=role.id,
        department_id=dept_id
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})

    token = create_access_token({"sub": user.email, "role": user.role.name, "user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login/json", response_model=Token)
def login_json(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": user.email, "role": user.role.name, "user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update current user's profile"""
    # Only update provided fields
    if update.name is not None:
        current_user.name = update.name
    if update.phone is not None:
        current_user.phone = update.phone
    if update.address is not None:
        current_user.address = update.address
    if update.age is not None:
        current_user.age = update.age
    if update.gender is not None:
        current_user.gender = update.gender
    if update.profile_picture is not None:
        current_user.profile_picture = update.profile_picture

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/upload-profile-picture")
async def upload_profile_picture(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Upload profile picture for current user and return updated path"""
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must be an image")

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image size must be less than 5MB")

    upload_dir = Path("uploads/profile_pictures")
    upload_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(file.filename or "profile.jpg").suffix
    timestamp = int(datetime.utcnow().timestamp())
    filename = f"profile_{current_user.id}_{timestamp}{extension}"
    file_path = upload_dir / filename

    with open(file_path, "wb") as f:
        f.write(content)

    # Save relative path to DB
    current_user.profile_picture = f"/uploads/profile_pictures/{filename}"
    db.commit()
    db.refresh(current_user)

    return {"profile_picture": current_user.profile_picture}
