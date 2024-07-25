from typing import List

from pydantic import BaseModel
from datetime import datetime
import uuid
from enum import Enum


class ProductType(BaseModel):
    types: List[str] = ["Soap", "Scrub", "Shower soap", "Bath bomb", "Solid shampoo"]


class ProductFlavour(BaseModel):
    flavours: List[str] = ["Mango", "Castile", "Avocado", "Nut"]


class CreateProduct(BaseModel):
    product_type: str
    title: str
    description: str
    price: int
    flavour: str
    weight: int

    class Config:
        validate_assignment = True


class Product(BaseModel):
    id: uuid.UUID
    product_type: str
    title: str
    description: str
    price: int
    flavour: str
    weight: int

    class Config:
        orm_mode = True


class Delete(BaseModel):
    message: str





