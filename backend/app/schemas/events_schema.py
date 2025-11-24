from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Response schema
class EventOut(BaseModel):
    event_id: int
    session_id: str
    customer_id: str
    article_id: str
    event_type: str
    campaign_id: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True

# Request schema
class EventCreate(BaseModel):
    session_id: str
    customer_id: str
    article_id: str
    event_type: str
    campaign_id: Optional[int]
