from sqlalchemy import Column, String, Integer
from app.postgress.database import Base
import uuid


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    product_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    instructions = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    flavour = Column(String, nullable=False)
    weight = Column(Integer, nullable=False)


class ProductTypeModel(Base):
    __tablename__ = "product_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)


class ProductFlavourModel(Base):
    __tablename__ = "product_flavours"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)

