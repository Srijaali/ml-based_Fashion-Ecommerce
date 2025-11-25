# app/core/auth.py

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db.database import get_db
from app.db.models.admins import Admin


# ============================================================
#  CONFIG
# ============================================================

JWT_SECRET = os.getenv("JWT_SECRET", os.getenv("SECRET_KEY", "supersecret-key-change-in-prod"))
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================
#  SECURITY SCHEME (Swagger uses this → shows single Bearer box)
# ============================================================

auth_scheme = HTTPBearer()


# ============================================================
#  PASSWORD HASHING
# ============================================================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================
#  JWT CREATION
# ============================================================

def create_access_token(
    data: Union[Dict[str, Any], int, str],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Creates a JWT token.
    Accepts either:
    - A dict → e.g. {"sub": "9", "type": "admin"}
    - An int/str (admin_id) → will create {"sub": str(admin_id), "type": "admin"}
    """
    if isinstance(data, (int, str)):
        # If admin_id is passed directly, create the payload
        to_encode = {"sub": str(data), "type": "admin"}
    else:
        # If dict is passed, use it (but ensure type is set)
        to_encode = data.copy()
        if "type" not in to_encode:
            to_encode["type"] = "admin"
    
    now = datetime.utcnow()

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"iat": now, "exp": expire})

    encoded = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded


# ============================================================
#  JWT DECODING
# ============================================================

def decode_access_token(token: str) -> dict:
    """
    Decodes the JWT token and returns its payload.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================
#  CURRENT ADMIN DEPENDENCY
# ============================================================

def get_current_admin(
    credentials=Depends(auth_scheme),
    db: Session = Depends(get_db)
):
    """
    Extracts admin from Bearer token.
    Used in protected admin endpoints.
    Returns Admin model (SQLAlchemy) which can be converted to AdminMe Pydantic model.
    """

    token = credentials.credentials  # raw JWT string
    payload = decode_access_token(token)

    admin_id = payload.get("sub")
    token_type = payload.get("type")

    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token type is admin
    if token_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        admin_id_int = int(admin_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: subject must be integer",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch admin from DB
    admin = db.query(Admin).filter(Admin.admin_id == admin_id_int).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return admin
