# schemas.py - Data validation shapes (what API accepts and returns)

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ─── User Schemas ─────────────────────────────────────────

class UserRegister(BaseModel):
    name: str
    email: str
    phone: str
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    district: Optional[str] = None
    age: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    username: Optional[str]
    phone: Optional[str]
    district: Optional[str]
    age: Optional[int]
    profile_picture: Optional[str]
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Complaint Schemas ────────────────────────────────────

class ComplaintCreate(BaseModel):
    citizen_name: str
    age: int
    district: str
    department: str
    subcategory: str
    description: str

class ComplaintResponse(BaseModel):
    id: int
    user_id: int
    citizen_name: str
    age: int
    district: str
    department: str
    subcategory: str
    description: str
    voice_file:    Optional[str]
    proof_doc:     Optional[str]    # ✅ proof document
    status: str
    admin_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StatusUpdate(BaseModel):
    status: str
    message: Optional[str] = None


# ─── Admin Schemas ────────────────────────────────────────

class AdminLogin(BaseModel):
    username: str
    password: str
    role: str


# ─── Token Schema ─────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    email: Optional[str] = None
    username: Optional[str] = None
    name: Optional[str] = None