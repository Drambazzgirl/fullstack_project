"""
Pydantic schemas for request/response validation
These define the structure of data coming in and going out of our API
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# ===== USER SCHEMAS =====
class UserBase(BaseModel):
    """Base user schema with common fields"""
    name: str
    email: EmailStr
    phone: Optional[str] = ""

class UserCreate(UserBase):
    """Schema for creating a new user (includes password)"""
    password: str

class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    profile_picture: Optional[str] = None

class UserResponse(UserBase):
    """Schema for user response (without password)"""
    id: int
    role_name: str
    department_id: Optional[int] = None
    address: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    profile_picture: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

# ===== ADMIN SCHEMAS =====
class AdminRegister(BaseModel):
    """Schema to register an admin (requires a secret)"""
    name: str
    email: EmailStr
    password: str
    admin_type: str  # 'c_admin' or 'cm_admin'
    department_id: Optional[int] = None
    registration_secret: Optional[str] = None

class AdminResponse(BaseModel):
    """Schema for admin response"""
    id: int
    name: str
    email: EmailStr
    role_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ===== COMPLAINT SCHEMAS =====
class ComplaintBase(BaseModel):
    """Base complaint schema"""
    department: str
    district: str
    subcategory: str
    title: str
    description: str

class ComplaintCreate(ComplaintBase):
    """Schema for creating a complaint"""
    location: Optional[str] = None

class ComplaintUpdate(BaseModel):
    """Schema for updating complaint status (admin only)"""
    status: Optional[str] = None
    admin_response: Optional[str] = None

class ComplaintResponse(ComplaintBase):
    """Schema for complaint response"""
    id: int
    user_id: int
    user_name: Optional[str] = None
    user_profile_picture: Optional[str] = None
    location: Optional[str] = None
    status: str
    admin_response: Optional[str] = None
    image_url: Optional[str] = None
    voice_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
    
class AdminComplaintResponse(ComplaintResponse):
    """Detailed complaint schema for admin view (includes user info)"""
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    user_email: Optional[str] = None
    
    class Config:
        from_attributes = True

# ===== MESSAGE SCHEMAS =====
class ComplaintMessageCreate(BaseModel):
    message: str

class ComplaintMessageResponse(BaseModel):
    id: int
    complaint_id: int
    sender_id: int
    message: str
    created_at: datetime
    sender_name: Optional[str] = None

    class Config:
        from_attributes = True

# ===== TOKEN SCHEMAS =====
class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for token data"""
    email: Optional[str] = None
    role: Optional[str] = None
    user_id: Optional[int] = None