"""
Main FastAPI application
This is the entry point for the backend server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.routers import auth, complaints, admin
import os

# Create database tables
Base.metadata.create_all(bind=engine)
print("[OK] Created database tables")

# Create default roles and admin users (using User model + Role)
from app.models import Role, User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.security import get_password_hash


def ensure_role_column_and_defaults():
    """Make sure `users.role_id` column exists and populate defaults for existing rows.

    This is a safe, idempotent startup helper to avoid failures when upgrading the schema
    without running migrations in development environments.
    """
    # Use an explicit connection and transactional block
    with engine.begin() as conn:
        # If model has new user columns, add them if missing (safe upgrades for dev)
        conn.execute(text("""
            DO $$
            BEGIN
                -- Add role_id
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='users' AND column_name='role_id'
                ) THEN
                    ALTER TABLE users ADD COLUMN role_id INTEGER;
                END IF;

                -- Add department_id
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='users' AND column_name='department_id'
                ) THEN
                    ALTER TABLE users ADD COLUMN department_id INTEGER;
                END IF;

                -- Add created_at and updated_at timestamps
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='users' AND column_name='created_at'
                ) THEN
                    ALTER TABLE users ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT now();
                END IF;
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='users' AND column_name='updated_at'
                ) THEN
                    ALTER TABLE users ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT now();
                END IF;

                -- Add profile_picture if missing
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='users' AND column_name='profile_picture'
                ) THEN
                    ALTER TABLE users ADD COLUMN profile_picture VARCHAR(255);
                END IF;

                -- Ensure phone column is nullable (for admin users)
                ALTER TABLE users ALTER COLUMN phone DROP NOT NULL;

            END;
            $$;
        """))

        # Ensure a 'user' role exists
        conn.execute(text("INSERT INTO roles (name) SELECT 'user' WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name='user')"))

        # Set role_id for any existing users to the 'user' role (use raw UPDATE to avoid ORM-managed timestamp side-effects)
        conn.execute(text("UPDATE users SET role_id = (SELECT id FROM roles WHERE name='user' LIMIT 1) WHERE role_id IS NULL"))

        # Optionally add a foreign key constraint if not present
        conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = 'users' AND kcu.column_name = 'role_id'
                ) THEN
                    ALTER TABLE users ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE SET NULL;
                END IF;

                -- Add FK for department_id if missing
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = 'users' AND kcu.column_name = 'department_id'
                ) THEN
                    ALTER TABLE users ADD CONSTRAINT users_department_id_fkey FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL;
                END IF;
            END;
            $$;
        """))


def create_default_roles_and_admins():
    """Ensure roles exist and create default C-Admin and CM-Admin users if missing"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        # Ensure standard roles exist
        for role_name in ("user", "c_admin", "cm_admin"):
            r = db.query(Role).filter(Role.name == role_name).first()
            if not r:
                db.add(Role(name=role_name))
        db.commit()

        # Ensure any existing users without a role get the 'user' role
        user_role = db.query(Role).filter(Role.name == "user").first()
        if user_role:
            try:
                # Use a raw UPDATE to avoid touching ORM-managed timestamps if the schema differs
                db.execute(text("UPDATE users SET role_id = :rid WHERE role_id IS NULL"), {"rid": user_role.id})
                db.commit()
            except Exception:
                # Best-effort: ignore if DB schema differs; seeding step should be idempotent
                db.rollback()

        # Default admins
        c_admin_email = "c.admin@voiceoftn.com"
        cm_admin_email = "cm.admin@voiceoftn.com"

        c_role = db.query(Role).filter(Role.name == "c_admin").first()
        cm_role = db.query(Role).filter(Role.name == "cm_admin").first()

        # Create C-Admin
        if not db.query(User).filter(User.email == c_admin_email).first():
            if c_role is None:
                raise RuntimeError("c_admin role not found after creation")
            db.add(User(
                name="C-Admin (Complaint Handler)",
                email=c_admin_email,
                password=get_password_hash("cadmin123"),
                role_id=c_role.id
            ))
            print("[OK] Created C-Admin user")
        else:
            print("[OK] C-Admin user already exists")

        # Create CM-Admin
        if not db.query(User).filter(User.email == cm_admin_email).first():
            if cm_role is None:
                raise RuntimeError("cm_admin role not found after creation")
            db.add(User(
                name="CM-Admin (Chief Manager)",
                email=cm_admin_email,
                password=get_password_hash("cmadmin123"),
                role_id=cm_role.id
            ))
            print("[OK] Created CM-Admin user")
        else:
            print("[OK] CM-Admin user already exists")

        db.commit()

    except Exception as e:
        print(f"Warning: Could not create default roles/admins: {e}")
    finally:
        db.close()

# Ensure upload directories exist
os.makedirs("uploads/profile_pictures", exist_ok=True)
os.makedirs("uploads/complaints", exist_ok=True)
os.makedirs("uploads/voice_recordings", exist_ok=True)

# Ensure role column and defaults before seeding admins
try:
    ensure_role_column_and_defaults()
except Exception as e:
    print(f"Warning: Could not ensure role column/defaults: {e}")

create_default_roles_and_admins()

# Create FastAPI app
app = FastAPI(
    title="Voice of TN API",
    description="Backend API for Voice of Tamil Nadu Complaint Management System",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(complaints.router)
app.include_router(admin.router)

@app.get("/")
def root():
    """Root endpoint - API health check"""
    return {
        "message": "Welcome to Voice of TN API v2.0",
        "status": "active",
        "version": "2.0.0",
        "admins": {
            "c_admin": "Complaint Handler - Can mark as Pending/In Progress",
            "cm_admin": "Chief Manager - Can mark as Solved"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}