# app/core/auth.py
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import jwt  # PyJWT
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models.admins import Admin  # your SQLAlchemy Admin model

# Config (override via env)
JWT_SECRET = os.getenv("JWT_SECRET", "rija123")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admins/login")  # used by OpenAPI

# replace existing hash/verify with this block

MAX_BCRYPT_INPUT_BYTES = 72

def _password_bytes(p: str) -> bytes:
    return p.encode("utf-8", errors="ignore")

def validate_password_length_or_400(p: str):
    if len(_password_bytes(p)) > MAX_BCRYPT_INPUT_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Password too long. Max {MAX_BCRYPT_INPUT_BYTES} bytes allowed; try a shorter password."
        )

def hash_password(plain: str) -> str:
    validate_password_length_or_400(plain)
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    # If it's too long, immediately fail auth to avoid bcrypt ValueError.
    if len(_password_bytes(plain)) > MAX_BCRYPT_INPUT_BYTES:
        return False
    return pwd_context.verify(plain, hashed)


# --- JWT helpers ---
def create_access_token(subject: str | int, expires_delta: Optional[timedelta] = None) -> str:
    now = datetime.utcnow()
    to_encode: Dict[str, Any] = {"sub": str(subject), "iat": now}
    if expires_delta:
        exp = now + expires_delta
    else:
        exp = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": exp})
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# --- Dependencies ---
def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Admin:
    payload = decode_access_token(token)
    admin_id = payload.get("sub")
    if not admin_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed token")
    admin = db.query(Admin).filter(Admin.admin_id == int(admin_id)).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found")
    if not admin.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin is inactive")
    return admin

# If you want explicit "superadmin" behavior, implement a second dependency that checks an `is_superadmin` column
def require_superadmin(current_admin=Depends(get_current_admin)):
    # TODO: upgrade DB model with is_superadmin boolean, then change this check:
    # if not current_admin.is_superadmin:
    #     raise HTTPException(status_code=403, detail="Requires superadmin")
    # for now all admins allowed
    return current_admin
