# customer_auth.py - Customer Authentication System

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
from typing import Optional
import os

from app.db.database import get_db

# JWT Configuration (same as admin)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================
# PYDANTIC MODELS
# ============================================

class CustomerSignup(BaseModel):
    age: int
    postal_code: str
    club_member_status: str
    fashion_news_frequency: str
    active: bool
    first_name: str
    last_name: str
    email: EmailStr
    gender: str
    loyalty_score: float
    password: str
    phone: Optional[str] = None
    address: Optional[str] = None

class CustomerLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class CustomerResponse(BaseModel):
    customer_id: str  # VARCHAR in database, so must be str
    email: str
    first_name: str
    last_name: str

# ============================================
# PASSWORD HASHING
# ============================================

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ============================================
# JWT TOKEN FUNCTIONS
# ============================================

def create_customer_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "customer"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ============================================
# GET CURRENT CUSTOMER DEPENDENCY
# ============================================

def get_current_customer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        customer_id: str = str(payload.get("sub"))  # Convert to string since it's VARCHAR in DB
        token_type: str = payload.get("type")
        
        if customer_id is None or token_type != "customer":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Fetch customer from database
    customer = db.execute(
        text("""
            SELECT customer_id, email, first_name, last_name 
            FROM niche_data.customers 
            WHERE customer_id = :customer_id
        """),
        {"customer_id": customer_id}
    ).fetchone()
    
    if customer is None:
        raise credentials_exception
    
    return CustomerResponse(
        customer_id=customer.customer_id,
        email=customer.email,
        first_name=customer.first_name,
        last_name=customer.last_name
    )

# ============================================
# CUSTOMER ROUTER
# ============================================

router = APIRouter(prefix="/customers/auth", tags=["Customer Auth"])

@router.post("/signup", response_model=Token)
def customer_signup(signup_data: CustomerSignup, db: Session = Depends(get_db)):
    """Customer signup endpoint"""
    
    # Check if email already exists
    existing = db.execute(
        text("SELECT customer_id FROM niche_data.customers WHERE email = :email"),
        {"email": signup_data.email}
    ).fetchone()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(signup_data.password)
    
    # Generate sequential customer_id: MAX(customer_id) + 1
    # customer_id is VARCHAR, but we'll treat numeric values as sequential
    # This handles both numeric strings and ensures sequential IDs
    max_id_result = db.execute(
        text("""
            SELECT MAX(
                CASE 
                    WHEN customer_id ~ '^[0-9]+$' THEN customer_id::bigint
                    ELSE 0
                END
            ) as max_numeric_id
            FROM niche_data.customers
        """)
    ).fetchone()
    
    # Get the maximum numeric customer_id, or start at 0 if no customers exist
    max_numeric_id = max_id_result[0] if max_id_result and max_id_result[0] is not None else 0
    
    # Generate next customer_id (max + 1)
    next_customer_id = str(max_numeric_id + 1)
    
    # Insert customer with the generated sequential ID
    result = db.execute(
        text("""
            INSERT INTO niche_data.customers (
                customer_id, age, postal_code, club_member_status, fashion_news_frequency, 
                active, first_name, last_name, email, signup_date, gender, loyalty_score,
                password_hash, phone, address
            )
            VALUES (
                :customer_id, :age, :postal_code, :club_member_status, :fashion_news_frequency, 
                :active, :first_name, :last_name, :email, :signup_date, :gender, :loyalty_score,
                :password_hash, :phone, :address
            )
            RETURNING customer_id
        """),{
            "customer_id": next_customer_id,
            "age": signup_data.age,
            "postal_code": signup_data.postal_code,
            "club_member_status": signup_data.club_member_status,
            "fashion_news_frequency": signup_data.fashion_news_frequency,
            "active": signup_data.active,
            "first_name": signup_data.first_name,
            "last_name": signup_data.last_name,
            "email": signup_data.email,
            "signup_date": datetime.utcnow(),
            "gender": signup_data.gender,
            "loyalty_score": signup_data.loyalty_score,
            "password_hash": hashed_password,
            "phone": signup_data.phone,
            "address": signup_data.address
        }
    ).fetchone()
    
    db.commit()
    
    # Get the customer_id from the result
    customer_id = result[0]
    
    # Create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_customer_token(
        data={"sub": str(customer_id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def customer_login(login_data: CustomerLogin, db: Session = Depends(get_db)):
    """Customer login endpoint"""
    
    # Get customer
    customer = db.execute(
        text("""
            SELECT customer_id, password_hash 
            FROM niche_data.customers 
            WHERE email = :email
        """),
        {"email": login_data.email}
    ).fetchone()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(login_data.password, customer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_customer_token(
        data={"sub": str(customer.customer_id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=CustomerResponse)
def get_current_customer_info(current_customer: CustomerResponse = Depends(get_current_customer)):
    """Get current logged-in customer info"""
    return current_customer