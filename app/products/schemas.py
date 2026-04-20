from typing import List

from pydantic import BaseModel
from datetime import datetime
import uuid
from enum import Enum


class ProductType(BaseModel):
    types: List[str]


class ProductFlavour(BaseModel):
    flavours: List[str]


class CreateProductType(BaseModel):
    name: str


class CreateProductFlavour(BaseModel):
    name: str


class CreateProduct(BaseModel):
    product_type: str
    title: str
    description: str
    instructions: str | None = None
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
    instructions: str | None = None
    price: int
    flavour: str
    weight: int

    class Config:
        from_attributes = True


class Delete(BaseModel):
    message: str





