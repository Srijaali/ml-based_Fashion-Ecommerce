# app/routers/admins.py
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import text
from app.db.database import get_db
from app.db.models.admins import Admin  # your SQLAlchemy model for admins
from app.schemas.admins_schema import (
    AdminCreate, AdminLogin, TokenResponse, AdminOut, AdminMe, ChangePasswordRequest
)
from app.core.auth import (
    hash_password, verify_password, create_access_token,
    get_current_admin, ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()

# helper to log admin actions to DB
def log_admin_action(db: Session, admin_id: int, action: str, details: dict | None = None):
    try:
        details_json = json.dumps(details or {})
        sql = """
            INSERT INTO niche_data.admin_activity_log (admin_id, action, details, created_at)
            VALUES (:admin_id, :action, :details::jsonb, NOW())
        """
        db.execute(text(sql), {"admin_id": admin_id, "action": action, "details": details_json})
        # Note: don't commit here; caller may be in larger transaction
    except Exception:
        # never raise here to avoid breaking admin action on logging failure
        pass


# ---------------- public: login ----------------
@router.post("/login", response_model=TokenResponse)
def login(payload: AdminLogin, db: Session = Depends(get_db)):
    print(f"Login attempt for: {payload.username_or_email}")
    
    # allow login by username or email
    ident = payload.username_or_email
    admin = db.query(Admin).filter(
        (Admin.username == ident) | (Admin.email == ident)
    ).first()
    
    print(f"Admin found: {admin is not None}")
    if admin:
        print(f"Admin active: {admin.is_active}")
        print(f"Password verification starting...")
        pwd_valid = verify_password(payload.password, admin.password_hash)
        print(f"Password valid: {pwd_valid}")
    
    if not admin or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Admin inactive"
        )

    # set last_login_at
    admin.last_login_at = datetime.utcnow()
    db.commit()
    
    # log login
    try:
        log_admin_action(db, admin.admin_id, "login", {"ip": None})
        db.commit()
    except Exception as e:
        print(f"Logging error: {e}")
        db.rollback()

    access_token = create_access_token(
        admin.admin_id, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES}
# ---------------- create admin (bootstrap) ----------------
@router.post("/", response_model=AdminOut, status_code=status.HTTP_201_CREATED)
def create_admin(payload: AdminCreate, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    """
    Create a new admin. For bootstrapping (no admins exist) you can remove the dependency.
    I kept it protected: only existing admins can create a new admin.
    """
    # uniqueness checks
    existing = db.query(Admin).filter((Admin.username == payload.username) | (Admin.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    hashed = hash_password(payload.password)
    ins_sql = text("""
        INSERT INTO niche_data.admins (username, email, password_hash, created_at, is_active)
        VALUES (:username, :email, :password_hash, NOW(), :is_active)
        RETURNING admin_id, username, email, created_at, last_login_at, is_active
    """)
    row = db.execute(ins_sql, {
        "username": payload.username,
        "email": payload.email,
        "password_hash": hashed,
        "is_active": payload.is_active
    }).mappings().first()
    db.commit()

    # log action
    try:
        log_admin_action(db, current_admin.admin_id, "create_admin", {"created_admin": row["admin_id"]})
        db.commit()
    except Exception:
        db.rollback()

    return row

# ---------------- list admins ----------------
@router.get("/", response_model=list[AdminOut])
def list_admins(db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    rows = db.execute(text("SELECT admin_id, username, email, created_at, last_login_at, is_active FROM niche_data.admins ORDER BY admin_id")).mappings().all()
    return rows

# ---------------- get me ----------------
@router.get("/me", response_model=AdminMe)
def me(current_admin = Depends(get_current_admin)):
    return current_admin

# ---------------- change password ----------------
@router.post("/change-password")
def change_password(payload: ChangePasswordRequest, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    if not verify_password(payload.old_password, current_admin.password_hash):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    new_hashed = hash_password(payload.new_password)
    current_admin.password_hash = new_hashed
    db.commit()

    # log
    try:
        log_admin_action(db, current_admin.admin_id, "change_password", None)
        db.commit()
    except Exception:
        db.rollback()

    return {"detail": "Password changed"}

# ---------------- logout (client-side) ----------------
@router.post("/logout")
def logout(current_admin = Depends(get_current_admin)):
    # token invalidation requires blacklist; here we simply log and let client discard the token
    # Implement token blacklist in DB if you want server-side invalidation.
    return {"detail": "Logged out (client must discard token)"}
