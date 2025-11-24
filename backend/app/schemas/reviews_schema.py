from pydantic import BaseModel
from datetime import datetime

# Response schema
class ReviewOut(BaseModel):
    review_id: int
    customer_id: str
    article_id: str
    rating: int
    review_text: str
    created_at: datetime

    class Config:
        orm_mode = True

# Request schema
class ReviewCreate(BaseModel):
    customer_id: str
    article_id: str
    rating: int
    review_text: str
