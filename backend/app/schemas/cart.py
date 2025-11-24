from pydantic import BaseModel
from datetime import datetime

# Response schema
class CartOut(BaseModel):
    cart_id: int
    customer_id: str
    article_id: str
    quantity: int
    added_at: datetime

    class Config:
        orm_mode = True

# Request schema
class CartCreate(BaseModel):
    customer_id: str
    article_id: str
    quantity: int
