from pydantic import BaseModel
from datetime import datetime, date



class OrderBase(BaseModel):
    order_id: int
    customer_id: str
    order_date: datetime
    total_amount: float
    payment_status: str
    shipping_address: str

    class Config:
        orm_mode = True

# Request schema
class OrderCreate(BaseModel):
    customer_id: str
    total_amount: float
    payment_status: str
    shipping_address: str

class OrderOut(OrderBase):
    pass