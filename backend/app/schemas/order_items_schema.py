from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class OrderItemBase(BaseModel):
    order_item_id: int
    order_id: int
    article_id: str
    quantity: int
    unit_price: float
    line_total: float

    class Config:
        orm_mode = True

# Request schema
class OrderItemCreate(BaseModel):
    order_id: int
    article_id: str
    quantity: int
    unit_price: float
    line_total: float

class OrderItemOut(OrderItemBase):
    pass