from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.database import engine, Base
from app.routers import auth, users, departments, complaints

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Voice of TN API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(departments.router)
app.include_router(complaints.router)

@app.get("/")
def root():
    return {"message": "Voice of TN backend running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
