# routers/admin.py - Admin login route

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import AdminLogin, Token
from utils import verify_password, create_token

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.post("/login", response_model=Token)
def admin_login(data: AdminLogin, db: Session = Depends(get_db)):
    """Login for c_admin and cm_admin"""
    user = db.query(User).filter(
        User.username == data.username,
        User.role     == data.role
    ).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_token({"user_id": user.id, "role": user.role, "username": user.username})
    return Token(
        access_token = token,
        token_type   = "bearer",
        role         = user.role,
        username     = user.username,
        name         = user.name
    )
