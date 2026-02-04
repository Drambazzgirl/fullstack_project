"""
Database models (tables) for VoiceOfTN Complaint Management System
These SQLAlchemy models define the schema and relationships for Users, Roles,
Departments, Complaints, Complaint messages/updates and status history.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SAEnum
from sqlalchemy.orm import relationship, Mapped
from datetime import datetime
from app.database import Base
from typing import Optional
import enum

# Enumerations
class ComplaintStatus(enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    solved = "solved"

# Core models
class Role(Base):
    """Roles table - defines user roles (user, cm_admin, c_admin)"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    users = relationship("User", back_populates="role", cascade="all, delete-orphan")

class Department(Base):
    """Departments table - e.g., Public Works, Water, Electricity"""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    complaints = relationship("Complaint", back_populates="department", cascade="all, delete-orphan")
    users = relationship("User", back_populates="department")

class User(Base):
    """Users table - stores normal users and admins (role determines capabilities)"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(15), nullable=True)  # Made nullable for admins
    password = Column(String(255), nullable=False)  # hashed password
    address = Column(Text, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    profile_picture = Column(String(255), nullable=True)

    # Foreign keys
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)  # for cm_admin

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    role = relationship("Role", back_populates="users")
    department = relationship("Department", back_populates="users")
    complaints = relationship("Complaint", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("ComplaintMessage", back_populates="sender", cascade="all, delete-orphan")
    status_changes = relationship("ComplaintStatusHistory", back_populates="changed_by_user", cascade="all, delete-orphan")

class Complaint(Base):
    """Complaints table - core entity"""
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(200), nullable=True)
    status = Column(SAEnum(ComplaintStatus), default=ComplaintStatus.pending, nullable=False)  # type: ComplaintStatus  # type: ignore

    # Optional location/categorization fields
    district = Column(String(100), nullable=True)
    subcategory = Column(String(100), nullable=True)

    # Optional: fields for media paths (images, voice recordings)
    image_path = Column(String(500), nullable=True)
    voice_path = Column(String(500), nullable=True)

    # Track which admin updated the complaint (email)
    updated_by_admin = Column(String(100), nullable=True)

    admin_response = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="complaints")
    department = relationship("Department", back_populates="complaints")
    messages = relationship("ComplaintMessage", back_populates="complaint", cascade="all, delete-orphan")
    status_history = relationship("ComplaintStatusHistory", back_populates="complaint", cascade="all, delete-orphan")

class ComplaintMessage(Base):
    """Messages / Comments on complaints (from users or admins)"""
    __tablename__ = "complaint_messages"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="messages")
    sender = relationship("User", back_populates="messages")

class ComplaintStatusHistory(Base):
    """Tracks every status change for a complaint (audit trail)"""
    __tablename__ = "complaint_status_history"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False, index=True)
    old_status = Column(SAEnum(ComplaintStatus), nullable=True)  # type: Optional[ComplaintStatus]  # type: ignore
    new_status = Column(SAEnum(ComplaintStatus), nullable=False)  # type: ComplaintStatus  # type: ignore
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    note = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="status_history")
    changed_by_user = relationship("User", back_populates="status_changes")