"""
STEP-BY-STEP SETUP GUIDE:

1. CREATE VIRTUAL ENVIRONMENT:
   cd backend
   python -m venv venv
   
2. ACTIVATE VIRTUAL ENVIRONMENT:
   Windows: venv\Scripts\activate
   Mac/Linux: source venv/bin/activate

3. INSTALL DEPENDENCIES:
   pip install -r requirements.txt

4. SETUP POSTGRESQL DATABASE:
   - Install PostgreSQL
   - Create database: CREATE DATABASE voiceoftn;
   - Update credentials in app/config.py

5. CREATE ADMIN USER (Run in Python):
   from app.database import SessionLocal
   from app.models import Admin
   from passlib.context import CryptContext
   
   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
   db = SessionLocal()
   
   admin = Admin(
       name="Admin",
       email="admin@voiceoftn.com",
       password=pwd_context.hash("admin123")
   )
   db.add(admin)
   db.commit()

6. RUN THE SERVER:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

7. ACCESS API DOCUMENTATION:
   http://localhost:8000/docs

API ENDPOINTS:
==============
Authentication:
- POST /api/auth/register - Register new user
- POST /api/auth/login - User login
- POST /api/auth/admin/login - Admin login

Complaints:
- POST /api/complaints/ - Create complaint
- GET /api/complaints/ - Get all complaints (with filters)
- GET /api/complaints/user/{email} - Get user complaints
- GET /api/complaints/{id} - Get specific complaint

Admin:
- PUT /api/admin/complaints/{id} - Update complaint status
- GET /api/admin/stats - Get dashboard statistics
"""