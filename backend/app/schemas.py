from pydantic import BaseModel
from typing import Optional


# ---------------- USER SCHEMAS ----------------
class UserCreate(BaseModel):
    full_name: str
    email: str
    phone: str
    password: str
    confirm_password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    address: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    is_admin: bool

    class Config:

        from_attributes = True


# ---------------- DEPARTMENT SCHEMAS ----------------
class DepartmentCreate(BaseModel):
    name: str


class DepartmentResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# ---------------- COMPLAINT SCHEMAS ----------------
class ComplaintSchema(BaseModel):
    title: str
    description: str
    department_id: int


class ComplaintResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    user_id: int
    department_id: int
    admin_response: Optional[str] = None

    class Config:
        from_attributes = True

class ComplaintUpdate(BaseModel):
    status: str
    admin_response: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
