from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models.cart import Cart
from app.schemas.cart import CartCreate, CartOut

router = APIRouter()

@router.get("/", response_model=List[CartOut])
def get_all_cart(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Cart).offset(skip).limit(limit).all()

@router.post("/", response_model=CartOut)
def add_cart(item: CartCreate, db: Session = Depends(get_db)):
    db_item = Cart(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{cart_id}", response_model=CartOut)
def update_cart(cart_id: int, item: CartCreate, db: Session = Depends(get_db)):
    db_item = db.query(Cart).filter(Cart.cart_id == cart_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{cart_id}")
def delete_cart(cart_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Cart).filter(Cart.cart_id == cart_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(db_item)
    db.commit()
    return {"detail": "Cart item deleted successfully"}
