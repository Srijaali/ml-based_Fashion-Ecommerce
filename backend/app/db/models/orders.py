from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey
from app.db.database import Base
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"
    __table_args__ = {"schema": "niche_data"}
    order_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(255), ForeignKey("customers.customer_id"))
    order_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float)
    payment_status = Column(String(100))
    shipping_address = Column(String(255))
