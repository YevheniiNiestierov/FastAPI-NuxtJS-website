from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.sqlite.database import Base


class CartModel(Base):
    __tablename__ = "carts"

    cart_id = Column(String, primary_key=True, index=True)
    total_price = Column(Float, default=0.0)

    items = relationship("CartItemModel", back_populates="cart", cascade="all, delete-orphan")


class CartItemModel(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(String, ForeignKey("carts.cart_id"))
    product_id = Column(String, ForeignKey("products.id"))  # Changed to products.id
    quantity = Column(Integer, default=1)

    cart = relationship("CartModel", back_populates="items")
    product = relationship("ProductModel")
