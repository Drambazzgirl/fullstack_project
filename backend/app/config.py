from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:AcademyRootPassword@localhost:5432/VoiceOfTN"
   
    
    # JWT Secret key (change this to a random secret key in production)
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 hours
    # Optional secret required to register admin users via the API
    ADMIN_REGISTRATION_SECRET: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()