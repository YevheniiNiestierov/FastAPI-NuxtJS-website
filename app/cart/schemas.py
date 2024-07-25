from typing import Optional, List, Union

from pydantic import BaseModel, Field
from datetime import datetime
from app.products.schemas import Product
from app.users.schemas import User
import uuid


class Cart(BaseModel):
    cart_id: uuid.UUID
    user_id: Optional[uuid.UUID] = Field(default=None, description="ID of the user who owns the cart")
    total_price: int
    products: List[Product]
    product_id: Optional[uuid.UUID] = Field(default=None, description="ID of the product")


    class Config:
        validate_assignment = True
        orm_mode = True




