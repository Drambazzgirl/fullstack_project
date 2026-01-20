from app.database import SessionLocal, engine
from app import models, auth
import os

def seed():
    db = SessionLocal()
    
    # 1. Create Departments if they don't exist
    departments = [
        "Electricity Board (TNEB)",
        "Water & Sewage (CMWSSB)",
        "Roads & Transportation",
        "Public Health",
        "Education Department",
        "Police Department",
        "Agriculture",
        "Women & Child Welfare"
    ]
    
    for dept_name in departments:
        exists = db.query(models.Department).filter(models.Department.name == dept_name).first()
        if not exists:
            db.add(models.Department(name=dept_name))
            print(f"Added department: {dept_name}")

    # 2. Create Admin User if doesn't exist
    admin_email = "admin@voiceoftn.com"
    exists = db.query(models.User).filter(models.User.email == admin_email).first()
    if not exists:
        admin_user = models.User(
            full_name="System Admin",
            email=admin_email,
            phone="0000000000",
            hashed_password=auth.get_password_hash("admin123"),
            is_admin=True
        )
        db.add(admin_user)
        print(f"Added admin user: {admin_email}")

    db.commit()
    db.close()

if __name__ == "__main__":
    print("Seeding database...")
    seed()
    print("Seeding complete.")
