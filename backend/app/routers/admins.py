# app/routers/admins.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
import json

from app.db.database import get_db
from app.db.models.admins import Admin
from app.schemas.admins_schema import (
    AdminCreate, AdminLogin, TokenResponse, AdminOut, AdminMe, ChangePasswordRequest
)
from app.core.auth import (
    create_access_token,
    get_current_admin,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()


# ===================================================================
# 🔹 HELPER: Log admin activity
# ===================================================================
def log_admin_action(db: Session, admin_id: int, action: str, details: dict | None = None):
    try:
        details_json = json.dumps(details or {})
        sql = text("""
            INSERT INTO niche_data.admin_activity_log (admin_id, action, details, created_at)
            VALUES (:admin_id, :action, :details::jsonb, NOW())
        """)
        db.execute(sql, {
            "admin_id": admin_id,
            "action": action,
            "details": details_json
        })
    except Exception as e:
        print(f"⚠ Logging failed: {e}")
        # do NOT raise — action should not fail because of logger


# ===================================================================
# 🔹 OAUTH2 TOKEN ENDPOINT (Swagger "Authorize" uses this)
# ===================================================================
@router.post("/token", response_model=TokenResponse)
def token(form_data: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    """
    Used by Swagger UI “Authorize” popup.
    Accepts: username + password
    Validates using DB crypt() function.
    """
    sql = text("""
        SELECT * FROM niche_data.admin_login(:u, :p)
    """)

    row = db.execute(sql, {
        "u": form_data.username,
        "p": form_data.password
    }).mappings().first()

    if not row:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(row["admin_id"])

    # log login
    try:
        log_admin_action(db, row["admin_id"], "login", None)
        db.commit()
    except:
        db.rollback()

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES
    }


# ===================================================================
# 🔹 JSON LOGIN (for frontend POST /admins/login)
# ===================================================================
@router.post("/login", response_model=TokenResponse)
def login(payload: AdminLogin, db: Session = Depends(get_db)):
    """
    JSON login endpoint for Admin Panel UI or frontend.
    """
    sql = text("""
        SELECT * FROM niche_data.admin_login(:u, :p)
    """)

    row = db.execute(sql, {
        "u": payload.username_or_email,
        "p": payload.password
    }).mappings().first()

    if not row:
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token(row["admin_id"])

    # log
    try:
        log_admin_action(db, row["admin_id"], "login", None)
        db.commit()
    except:
        db.rollback()

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES
    }


# ===================================================================
# 🔹 CREATE ADMIN (Protected)
# ===================================================================
@router.post("/", response_model=AdminOut, status_code=201)
def create_admin(payload: AdminCreate,
                 db: Session = Depends(get_db),
                 current_admin: Admin = Depends(get_current_admin)):
    """
    Create a new admin.
    NOTE: Password hashing done inside DB with crypt().
    """
    # check duplicate
    exists = db.query(Admin).filter(
        (Admin.username == payload.username) |
        (Admin.email == payload.email)
    ).first()

    if exists:
        raise HTTPException(400, "Username or email already exists")

    sql = text("""
        INSERT INTO niche_data.admins (username, email, password_hash, created_at, is_active)
        VALUES (:u, :e, crypt(:p, gen_salt('bf')), NOW(), :active)
        RETURNING admin_id, username, email, created_at, last_login_at, is_active
    """)

    row = db.execute(sql, {
        "u": payload.username,
        "e": payload.email,
        "p": payload.password,
        "active": payload.is_active,
    }).mappings().first()

    # log
    try:
        log_admin_action(db, current_admin.admin_id, "create_admin",
                         {"created_admin": row["admin_id"]})
        db.commit()
    except:
        db.rollback()

    return row


# ===================================================================
# 🔹 LIST ADMINS (Protected)
# ===================================================================
@router.get("/", response_model=list[AdminOut])
def list_admins(db: Session = Depends(get_db),
                current_admin: Admin = Depends(get_current_admin)):
    sql = text("""
        SELECT admin_id, username, email, created_at, last_login_at, is_active
        FROM niche_data.admins
        ORDER BY admin_id
    """)
    return db.execute(sql).mappings().all()


# ===================================================================
# 🔹 ME (Protected)
# ===================================================================
@router.get("/me", response_model=AdminMe)
def me(current_admin: Admin = Depends(get_current_admin)):
    return current_admin


# ===================================================================
# 🔹 CHANGE PASSWORD (Protected)
# ===================================================================
@router.post("/change-password")
def change_password(payload: ChangePasswordRequest,
                    db: Session = Depends(get_db),
                    current_admin: Admin = Depends(get_current_admin)):
    # verify old password using DB
    sql = text("""
        SELECT * FROM niche_data.admin_login(:u, :p)
    """)

    check = db.execute(sql, {
        "u": current_admin.username,
        "p": payload.old_password
    }).mappings().first()

    if not check:
        raise HTTPException(400, "Old password incorrect")

    # update password using crypt()
    upd = text("""
        UPDATE niche_data.admins
        SET password_hash = crypt(:newp, gen_salt('bf'))
        WHERE admin_id = :aid
    """)

    db.execute(upd, {
        "newp": payload.new_password,
        "aid": current_admin.admin_id
    })

    # log
    try:
        log_admin_action(db, current_admin.admin_id, "change_password", None)
        db.commit()
    except:
        db.rollback()

    return {"detail": "Password changed successfully"}


# ===================================================================
# 🔹 LOGOUT (Client just discards token)
# ===================================================================
@router.post("/logout")
def logout(current_admin: Admin = Depends(get_current_admin)):
    return {"detail": "Logged out. Please discard the token."}
