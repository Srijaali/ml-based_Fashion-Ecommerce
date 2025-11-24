from pydantic import BaseModel
from datetime import date

# Response schema
class TransactionOut(BaseModel):
    transaction_id: int
    t_dat: date
    customer_id: str
    article_id: str
    price: float
    sales_channel_id: int

    class Config:
        orm_mode = True

# Request schema
class TransactionCreate(BaseModel):
    t_dat: date
    customer_id: str
    article_id: str
    price: float
    sales_channel_id: int
