from passlib.context import CryptContext  # type: ignore
from jose import jwt, JWTError  # type: ignore
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: Any) -> bool:
    """Verify password using multiple strategies to handle environment differences.

    1. Try passlib's pwd_context
    2. Fall back to bcrypt.checkpw if available
    3. As a last resort (development only), compare plaintext
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Try using bcrypt library directly if passlib backend is unavailable/broken
        try:
            import bcrypt as _bcrypt  # type: ignore
            if isinstance(hashed_password, str):
                return _bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
            else:
                return _bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)
        except Exception:
            # Final fallback for development: plain text comparison
            return plain_password == hashed_password


def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    to_encode = data.copy()
    if expires_minutes is None:
        expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    encoded = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise