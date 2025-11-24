from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models.wishlist import Wishlist
from app.schemas.wishlist import WishlistCreate, WishlistOut

router = APIRouter()

@router.get("/", response_model=List[WishlistOut])
def get_all_wishlist(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Wishlist).offset(skip).limit(limit).all()


@router.get("/{wishlist_id}", response_model=WishlistOut)
def get_wishlist(wishlist_id: str, db: Session = Depends(get_db)):
    db_wishlist = db.query(Wishlist).filter(Wishlist.wishlist_id == wishlist_id).first()
    if not db_wishlist:
        raise HTTPException(status_code=404, detail="wishlist not found")
    return db_wishlist

@router.post("/", response_model=WishlistOut)
def add_wishlist(item: WishlistCreate, db: Session = Depends(get_db)):
    db_item = Wishlist(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{wishlist_id}")
def delete_wishlist(wishlist_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Wishlist).filter(Wishlist.wishlist_id == wishlist_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    db.delete(db_item)
    db.commit()
    return {"detail": "Wishlist item deleted successfully"}
