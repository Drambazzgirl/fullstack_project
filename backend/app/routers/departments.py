from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models
from app.database import get_db


router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("/")
def list_departments(db: Session = Depends(get_db)):
    return db.query(models.Department).all()