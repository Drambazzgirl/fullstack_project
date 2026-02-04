#!/usr/bin/env python3
"""
Database initialization script for PostgreSQL
Run this script to create the database tables
"""

from app.database import engine, Base
from app.models import User, Admin, Complaint
import sys

def init_database():
    """Initialize the database by creating all tables"""
    try:
        print("🔄 Creating database tables...")

        # Create all tables
        Base.metadata.create_all(bind=engine)

        print("✅ Database tables created successfully!")

        # Create default admin user
        from app.database import SessionLocal
        from app.routers.auth import hash_password

        db = SessionLocal()
        try:
            # Check if admin already exists
            existing_admin = db.query(Admin).filter(Admin.email == "admin@voiceoftn.com").first()
            if not existing_admin:
                # Create default admin
                default_admin = Admin(
                    name="System Admin",
                    email="admin@voiceoftn.com",
                    password=hash_password("admin123")
                )
                db.add(default_admin)
                db.commit()
                print("✅ Default admin user created!")
                print("   Email: admin@voiceoftn.com")
                print("   Password: admin123")
            else:
                print("ℹ️  Default admin user already exists")

        except Exception as e:
            print(f"⚠️  Warning: Could not create default admin: {e}")
        finally:
            db.close()

    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()