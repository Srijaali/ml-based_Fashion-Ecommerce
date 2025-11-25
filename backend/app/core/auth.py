# app/core/auth.py
import os
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models.admins import Admin
# at top of app/core/auth.py
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# replace oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admins/token")
# with:
bearer_scheme = HTTPBearer()   # used by Swagger to show single "Bearer <token>" box

JWT_SECRET = os.getenv("JWT_SECRET", "rija-super-secret")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admins/token")


# -------------- JWT Helpers ----------------

def create_access_token(admin_id: int):
    now = datetime.utcnow()
    payload = {
        "sub": str(admin_id),
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> Admin:
    """
    Accepts an HTTP Bearer token from Authorization header (Swagger will show a simple Bearer input).
    """
    token = credentials.credentials if credentials else None
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_token(token)

    admin_id = payload.get("sub")
    if not admin_id:
        raise HTTPException(status_code=401, detail="Invalid token: missing subject")

    try:
        admin_id_int = int(admin_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token: malformed subject")

    admin = db.query(Admin).filter(Admin.admin_id == admin_id_int).first()
    if not admin:
        raise HTTPException(status_code=401, detail="Admin not found")

    if not admin.is_active:
        raise HTTPException(status_code=403, detail="Admin account is inactive")

    return admin

