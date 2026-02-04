"""
Create default admin users for C-Admin and CM-Admin roles
"""
from app.database import engine, SessionLocal
from app.models import Admin
from app.routers.auth import hash_password

def create_default_admins():
    db = SessionLocal()
    try:
        # Define default admins
        admins_to_create = [
            {
                "name": "Arun Kumar",
                "email": "c_admin@voiceoftn.com",
                "password": "admin123",
                "admin_type": "c_admin"
            },
            {
                "name": "Meera Selvan",
                "email": "cm_admin@voiceoftn.com",
                "password": "admin123",
                "admin_type": "cm_admin"
            }
        ]

        for admin_data in admins_to_create:
            # Check if admin already exists
            existing_admin = db.query(Admin).filter(Admin.email == admin_data["email"]).first()
            if existing_admin:
                print(f"Admin already exists: {admin_data['email']} ({admin_data['admin_type']})")
                continue

            # Create new admin
            new_admin = Admin(
                name=admin_data["name"],
                email=admin_data["email"],
                password=hash_password(admin_data["password"]),
                admin_type=admin_data["admin_type"]
            )

            db.add(new_admin)
            print(f"✓ Created {admin_data['admin_type']}: {admin_data['email']}")

        db.commit()
        print("\nAll default admins processed successfully!")
        
    except Exception as e:
        print(f"Error creating admins: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_default_admins()