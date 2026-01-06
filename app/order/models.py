from sqlalchemy import Column, String, Integer, DateTime, JSON
from app.sqlite.database import Base
from datetime import datetime


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    delivery_type = Column(String, nullable=False)
    city = Column(String, nullable=False)
    department_number = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    products = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_sum = Column(Integer, nullable=False)
    user_id = Column(String, nullable=False)
