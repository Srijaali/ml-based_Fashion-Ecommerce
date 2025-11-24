from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models.order_items import OrderItem
from app.schemas.order_items_schema import OrderItemCreate, OrderItemOut

router = APIRouter()

@router.get("/", response_model=List[OrderItemOut])
def get_all_order_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(OrderItem).offset(skip).limit(limit).all()



@router.get("/{order_item_id}", response_model=OrderItemOut)
def get_order_item(order_item_id: str, db: Session = Depends(get_db)):
    db_order_item = db.query(OrderItem).filter(OrderItem.order_item_id == order_item_id).first()
    if not db_order_item:
        raise HTTPException(status_code=404, detail="Orfer ITem not found")
    return db_order_item

@router.post("/", response_model=OrderItemOut)
def add_order_item(order_item: OrderItemCreate, db: Session = Depends(get_db)):
    db_item = OrderItem(**order_item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{order_item_id}", response_model=OrderItemOut)
def update_order_item(order_item_id: int, order_item: OrderItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(OrderItem).filter(OrderItem.order_item_id == order_item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Order item not found")
    for key, value in order_item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{order_item_id}")
def delete_order_item(order_item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(OrderItem).filter(OrderItem.order_item_id == order_item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Order item not found")
    db.delete(db_item)
    db.commit()
    return {"detail": "Order item deleted successfully"}
