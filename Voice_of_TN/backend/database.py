# database.py - PostgreSQL connection setup

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Get database URL from .env file
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:AcademyRootPassword@localhost:5432/voice_of_tn")

# Create database engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# Dependency - gives a database session to each API request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
