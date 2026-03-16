from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine, Base
from routers import auth, complaints, admin
import os

# Create all database tables
Base.metadata.create_all(bind=engine)

# Seed admin users
from seed import seed_admins
seed_admins()

# Create FastAPI app
app = FastAPI(title="Voice of TN API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_BASE = "/tmp/uploads" if os.environ.get("RENDER") else "uploads"
os.makedirs(f"{UPLOAD_BASE}/voices", exist_ok=True)
os.makedirs(f"{UPLOAD_BASE}/profiles", exist_ok=True)
os.makedirs(f"{UPLOAD_BASE}/proofs", exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_BASE), name="uploads")

app.include_router(auth.router)
app.include_router(complaints.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "Voice of TN API is running!"}