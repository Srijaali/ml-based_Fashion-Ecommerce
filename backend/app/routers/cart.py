from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import text
from app.db.database import get_db
from app.db.models.cart import Cart
from app.schemas.cart import (
    CartItemBase,
    CartItemCreate,
    CartItemOut,
    CartItemUpdate,
    CartResponse,
)
router = APIRouter()

@router.get("/", response_model=List[CartItemBase])
def get_all_cart(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Cart).offset(skip).limit(limit).all()

@router.get("/{customer_id}", response_model=CartResponse)
def get_cart(customer_id: str, db: Session = Depends(get_db)):
    """
    Return full cart for a customer (all items).
    """
    sql = text("""
        SELECT cart_id, customer_id, article_id, quantity, added_at
        FROM niche_data.cart
        WHERE customer_id = :cid
        ORDER BY added_at DESC, cart_id
    """)
    rows = db.execute(sql, {"cid": customer_id}).mappings().all()
    return {"customer_id": customer_id, "items": rows}


# Add item to cart (merge if exists)
# -------------------------
@router.post("/", response_model=CartItemOut, status_code=status.HTTP_201_CREATED)
def add_to_cart(payload: CartItemCreate, db: Session = Depends(get_db)):
    """
    Add an item to cart. If the same article already exists in the customer's cart,
    the quantity will be incremented (merged). Returns the upserted cart row.
    """
    try:
        with db.begin():
            # check existing
            sql_select = text("""
                SELECT cart_id, customer_id, article_id, quantity, added_at
                FROM niche_data.cart
                WHERE customer_id = :cid AND article_id = :aid
                FOR UPDATE
            """)
            existing = db.execute(sql_select, {"cid": payload.customer_id, "aid": payload.article_id}).mappings().first()

            if existing:
                # merge quantity
                new_qty = int(existing["quantity"]) + int(payload.quantity)
                sql_update = text("""
                    UPDATE niche_data.cart
                    SET quantity = :qty, added_at = NOW()
                    WHERE cart_id = :cid
                    RETURNING cart_id, customer_id, article_id, quantity, added_at
                """)
                row = db.execute(sql_update, {"qty": new_qty, "cid": existing["cart_id"]}).mappings().first()
            else:
                # insert new item
                sql_insert = text("""
                    INSERT INTO niche_data.cart (customer_id, article_id, quantity, added_at)
                    VALUES (:cid, :aid, :qty, NOW())
                    RETURNING cart_id, customer_id, article_id, quantity, added_at
                """)
                row = db.execute(sql_insert, {"cid": payload.customer_id, "aid": payload.article_id, "qty": payload.quantity}).mappings().first()

        if not row:
            raise HTTPException(status_code=500, detail="Failed to add item to cart")

        return row

    except Exception as e:
        # keep the error message short for the client and log detailed error server-side
        raise HTTPException(status_code=400, detail=str(e))

# -------------------------
# Update quantity for a cart item
# ------------------------- edits existing cart item
@router.put("/{cart_id}", response_model=CartItemOut)
def update_cart_item(cart_id: int, payload: CartItemUpdate, db: Session = Depends(get_db)):
    """
    Update the quantity for a cart item by cart_id.
    """
    sql = text("""
        UPDATE niche_data.cart
        SET quantity = :qty, added_at = NOW()
        WHERE cart_id = :cid
        RETURNING cart_id, customer_id, article_id, quantity, added_at
    """)
    row = db.execute(sql, {"qty": int(payload.quantity), "cid": cart_id}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.commit()
    return row


# -------------------------
# Remove an item from cart
# -------------------------
@router.delete("/{cart_id}")
def remove_cart_item(cart_id: int, db: Session = Depends(get_db)):
    """
    Delete a cart by cart_id.
    """
    sql = text("DELETE FROM niche_data.cart WHERE cart_id = :cid RETURNING cart_id")
    row = db.execute(sql, {"cid": cart_id}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.commit()
    return {"detail": "Cart removed", "cart_id": row["cart_id"]}


# -------------------------
# Clear full cart for a customer
# -------------------------
@router.delete("/clear/{customer_id}")
def clear_cart(customer_id: str, db: Session = Depends(get_db)):
    """
    Remove all items from a customer's cart.
    """
    sql = text("DELETE FROM niche_data.cart WHERE customer_id = :cid RETURNING count(*)")
    # Note: returning count(*) from DELETE is not standard; do a separate count if needed
    deleted = db.execute(text("DELETE FROM niche_data.cart WHERE customer_id = :cid"), {"cid": customer_id})
    db.commit()
    return {"detail": "Cart cleared", "customer_id": customer_id}



# -------------------------
# Cart item count quick endpoint
# -------------------------
@router.get("/{customer_id}/count")
def cart_count(customer_id: str, db: Session = Depends(get_db)):
    sql = text("""
        SELECT COALESCE(SUM(quantity),0) AS total_items, COUNT(*) AS rows
        FROM niche_data.cart
        WHERE customer_id = :cid
    """)
    row = db.execute(sql, {"cid": customer_id}).mappings().first()
    return {"customer_id": customer_id, "total_items": int(row["total_items"]), "rows": int(row["rows"])}















'''
@router.post("/", response_model=CartItemBase)
def add_cart(item: CartItemCreate, db: Session = Depends(get_db)):
    db_item = Cart(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{cart_id}", response_model=CartItemBase)
def update_cart(cart_id: int, item: CartItemCreate, db: Session = Depends(get_db)):
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
'''