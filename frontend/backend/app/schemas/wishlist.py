from pydantic import BaseModel
from datetime import datetime

# Response schema
class WishlistOut(BaseModel):
    wishlist_id: int
    customer_id: str
    article_id: str
    added_at: datetime

    class Config:
        orm_mode = True

# Request schema
class WishlistCreate(BaseModel):
    customer_id: str
    article_id: str
