# models.py - Database table definitions

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    """
    Stores all users: citizens, c_admin, cm_admin
    """
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String(100), nullable=False)
    email           = Column(String(100), unique=True, nullable=True)
    username        = Column(String(100), unique=True, nullable=True)
    phone           = Column(String(15),  nullable=True)
    password_hash   = Column(String(255), nullable=False)
    district        = Column(String(100), nullable=True)
    age             = Column(Integer,     nullable=True)
    profile_picture = Column(String(255), nullable=True)
    role            = Column(String(20),  default="citizen")
    created_at      = Column(DateTime,    server_default=func.now())

    complaints = relationship("Complaint", back_populates="user")


class Complaint(Base):
    """
    Stores all complaints raised by citizens
    """
    __tablename__ = "complaints"

    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    citizen_name  = Column(String(100), nullable=False)
    age           = Column(Integer,     nullable=False)
    district      = Column(String(100), nullable=False)
    department    = Column(String(150), nullable=False)
    subcategory   = Column(String(150), nullable=False)
    description   = Column(Text,        nullable=False)
    voice_file    = Column(String(255), nullable=True)
    proof_doc     = Column(String(255), nullable=True)   # ✅ proof document path
    status        = Column(String(30),  default="pending")
    admin_message = Column(Text,        nullable=True)
    created_at    = Column(DateTime,    server_default=func.now())
    updated_at    = Column(DateTime,    server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="complaints")