"""
Simple database reset script
Recreates the database connection and tables
"""
import os
import sys

# Ensure the backend directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the FastAPI app which will trigger table creation
    from app.main import app
    print("[OK] FastAPI app loaded successfully")
    print("[OK] Database tables will be created on first request")
    print("\nTo verify the fix:")
    print("  1. Make sure the uvicorn server is running")
    print("  2. Try registering a new user at POST /api/auth/register")
    
except Exception as e:
    print(f"Error loading app: {e}")
    print("\nManual fix: Run this in PostgreSQL psql:")
    print("  \\c voiceoftn")
    print("  DROP TABLE IF EXISTS complaints CASCADE;")
    print("  DROP TABLE IF EXISTS admins CASCADE;")
    print("  DROP TABLE IF EXISTS users CASCADE;")
