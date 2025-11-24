from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import text
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


# ---------------- Get wishlist for 1 customer ----------------
@router.get("/customer/{customer_id}", response_model=List[WishlistOut])
def get_customer_wishlist(customer_id: str, db: Session = Depends(get_db)):
    sql = text("""
        SELECT wishlist_id, customer_id, article_id, added_at
        FROM niche_data.wishlist
        WHERE customer_id = :cid
        ORDER BY added_at DESC
    """)
    return db.execute(sql, {"cid": customer_id}).mappings().all()


# ---------------- Add item to wishlist ----------------
@router.post("/", response_model=WishlistOut)
def add_to_wishlist(payload: WishlistCreate, db: Session = Depends(get_db)):
    # 1. Check if already exists
    existing = db.execute(text("""
        SELECT wishlist_id, customer_id, article_id, added_at
        FROM niche_data.wishlist
        WHERE customer_id = :cid AND article_id = :aid
    """), {"cid": payload.customer_id, "aid": payload.article_id}).mappings().first()

    if existing:
        # OPTIONAL: Update timestamp if user clicks wishlist again
        updated = db.execute(text("""
            UPDATE niche_data.wishlist
            SET added_at = NOW()
            WHERE wishlist_id = :wid
            RETURNING wishlist_id, customer_id, article_id, added_at
        """), {"wid": existing["wishlist_id"]}).mappings().first()
        db.commit()
        return updated

    # 2. Insert new wishlist entry
    inserted = db.execute(text("""
        INSERT INTO niche_data.wishlist (customer_id, article_id, added_at)
        VALUES (:cid, :aid, NOW())
        RETURNING wishlist_id, customer_id, article_id, added_at
    """), {"cid": payload.customer_id, "aid": payload.article_id}).mappings().first()

    db.commit()
    return inserted

@router.post("/move-to-cart/{wishlist_id}")
def move_wishlist_to_cart(wishlist_id: int, db: Session = Depends(get_db)):
    # 1. Get wishlist item
    wl = db.execute(
        text("""
            SELECT wishlist_id, customer_id, article_id
            FROM niche_data.wishlist
            WHERE wishlist_id = :wid
        """),
        {"wid": wishlist_id}
    ).mappings().first()

    if not wl:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    customer_id = wl["customer_id"]
    article_id = wl["article_id"]

    # 2. Check if same article is already in cart
    existing = db.execute(
        text("""
            SELECT cart_id, quantity
            FROM niche_data.cart
            WHERE customer_id = :cid AND article_id = :aid
        """),
        {"cid": customer_id, "aid": article_id}
    ).mappings().first()

    if existing:
        # 3A. Update quantity (+1)
        new_qty = existing["quantity"] + 1
        db.execute(
            text("""
                UPDATE niche_data.cart
                SET quantity = :q
                WHERE cart_id = :cart_id
            """),
            {"q": new_qty, "cart_id": existing["cart_id"]}
        )
    else:
        # 3B. Insert new cart row
        db.execute(
            text("""
                INSERT INTO niche_data.cart (customer_id, article_id, quantity, added_at)
                VALUES (:cid, :aid, 1, NOW())
            """),
            {"cid": customer_id, "aid": article_id}
        )

    # 4. Delete from wishlist
    db.execute(
        text("DELETE FROM niche_data.wishlist WHERE wishlist_id = :wid"),
        {"wid": wishlist_id}
    )

    db.commit()

    return {"detail": "Item moved from wishlist to cart successfully"}

# ---------------- Delete specific wishlist item ----------------
@router.delete("/{wishlist_id}")
def delete_wishlist_item(wishlist_id: int, db: Session = Depends(get_db)):
    row = db.execute(text("""
        DELETE FROM niche_data.wishlist
        WHERE wishlist_id = :wid
        RETURNING wishlist_id
    """), {"wid": wishlist_id}).fetchone()

    db.commit()

    if not row:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    return {"detail": "Wishlist item deleted"}


# ---------------- Clear entire wishlist for customer ----------------
@router.delete("/customer/{customer_id}")
def clear_customer_wishlist(customer_id: str, db: Session = Depends(get_db)):
    db.execute(text("""
        DELETE FROM niche_data.wishlist
        WHERE customer_id = :cid
    """), {"cid": customer_id})
    
    db.commit()
    return {"detail": "Wishlist cleared"}



















'''
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
'''