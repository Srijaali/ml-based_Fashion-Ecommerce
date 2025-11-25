# app/core/auth.py
import os
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models.admins import Admin

JWT_SECRET = os.getenv("JWT_SECRET", "rija-super-secret")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admins/login")


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



def get_current_admin(token: str = Depends(oauth2_scheme),
                      db: Session = Depends(get_db)):
    payload = decode_token(token)
    admin_id = int(payload["sub"])
    admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
    if not admin:
        raise HTTPException(401, "Invalid admin")
    if not admin.is_active:
        raise HTTPException(403, "Admin inactive")
    return admin
