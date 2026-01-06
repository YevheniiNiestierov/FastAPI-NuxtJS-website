from sqlalchemy import Column, String, Integer
from app.sqlite.database import Base
import uuid


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    product_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    flavour = Column(String, nullable=False)
    weight = Column(Integer, nullable=False)
