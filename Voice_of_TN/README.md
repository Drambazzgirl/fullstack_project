# Voice of TN — Citizen Complaint Portal

A full-stack complaint management system for Tamil Nadu citizens.

---

## Tech Stack
- **Frontend**: HTML, CSS, JavaScript (Beginner-friendly)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL

---

## Folder Structure
```
Voice_of_TN/
├── frontend/
│   ├── index.html              ← Home page (public)
│   ├── login.html              ← Citizen login
│   ├── register.html           ← Citizen register
│   ├── profile.html            ← User dashboard
│   ├── complaint.html          ← Raise complaint
│   ├── complaints_view.html    ← View all complaints (public)
│   ├── admin_login.html        ← Admin login
│   ├── c_admin_dashboard.html  ← Department admin
│   ├── cm_admin_dashboard.html ← CM admin
│   ├── css/
│   │   ├── main.css            ← Shared styles
│   │   ├── index.css           ← Home page styles
│   │   ├── auth.css            ← Login/Register styles
│   │   ├── profile.css         ← Profile page styles
│   │   ├── complaint.css       ← Complaint form styles
│   │   ├── complaints_view.css ← All complaints styles
│   │   └── admin.css           ← Admin dashboard styles
│   └── js/
│       ├── config.js           ← API URL + shared helpers
│       ├── home.js
│       ├── register.js
│       ├── login.js
│       ├── profile.js
│       ├── complaint.js
│       ├── complaints_view.js
│       ├── admin_login.js
│       ├── c_admin.js
│       └── cm_admin.js
└── backend/
    ├── main.py                 ← FastAPI app entry
    ├── database.py             ← DB connection
    ├── models.py               ← DB tables
    ├── schemas.py              ← API data shapes
    ├── utils.py                ← Password + JWT helpers
    ├── routers/
    │   ├── auth.py             ← /api/auth/* routes
    │   ├── complaints.py       ← /api/complaints/* routes
    │   └── admin.py            ← /api/admin/* routes
    ├── seed.py                 ← Create admin accounts
    ├── requirements.txt
    └── .env.example
```

---

## Setup Instructions

### 1. PostgreSQL — Create Database
```sql
CREATE DATABASE voice_of_tn;
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Copy and edit .env
cp .env.example .env
# Edit .env: set your DB username/password

# Start server
uvicorn main:app --reload --port 8000
```

### 3. Create Admin Accounts (run ONCE)
```bash
cd backend
python seed.py
```
Admin credentials:
- **c_admin**  → username: `cadmin`   | password: `cadmin@123`
- **cm_admin** → username: `cmadmin`  | password: `cmadmin@123`

### 4. Frontend
Open `frontend/index.html` in browser.  
Or use VS Code Live Server extension.

---

## User Roles

| Role     | Access |
|----------|--------|
| citizen  | Register, Login, Raise Complaint, View Profile |
| c_admin  | View all complaints, Set In Progress / Completed |
| cm_admin | All of above + Mark as Solved with message |

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | /api/auth/register | Register citizen |
| POST | /api/auth/login/json | Login citizen |
| GET  | /api/auth/me | Get profile |
| PUT  | /api/auth/me | Update profile |
| POST | /api/auth/upload-profile-picture | Upload pic |
| POST | /api/complaints/ | Raise complaint |
| GET  | /api/complaints/ | Get all complaints (filters) |
| GET  | /api/complaints/my | Get my complaints |
| PUT  | /api/complaints/{id}/status | Update status (admin) |
| POST | /api/admin/login | Admin login |

---

## Districts Supported
Chennai, Chengalpattu, Kanchipuram, Vellore, Ranipet, Tirupattur,
Tiruvannamalai, Krishnagiri, Dharmapuri, Kallakurichi, Villupuram
