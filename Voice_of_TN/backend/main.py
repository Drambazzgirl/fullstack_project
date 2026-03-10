# main.py - FastAPI application entry point

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine, Base
from routers import auth, complaints, admin
import os

# Create all database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(title="Voice of TN API", version="1.0.0")

# Allow frontend to call this API (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files (profile pics, voice recordings)
os.makedirs("uploads/voices", exist_ok=True)
os.makedirs("uploads/profiles", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Register all route groups
app.include_router(auth.router)
app.include_router(complaints.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "Voice of TN API is running!"}
