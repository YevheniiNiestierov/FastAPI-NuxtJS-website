from typing import Optional, Dict, List, Union
from pydantic import BaseModel
import uuid


class ProductType(BaseModel):
    types: List[str]


class ProductFlavour(BaseModel):
    flavours: List[str]


class CreateProductType(BaseModel):
    name: str


class CreateProductFlavour(BaseModel):
    name: str

CharacteristicValue = Union[str, List[str]]

class CreateProduct(BaseModel):
    product_type: str
    title: str
    slug: Optional[str] = None
    description: str
    instructions: Optional[str] = None
    characteristics: Optional[Dict[str, CharacteristicValue]] = None
    price: int
    flavour: str
    weight: int

    class Config:
        validate_assignment = True


class Product(BaseModel):
    id: str
    product_type: str
    title: str
    slug: Optional[str] = None
    description: str
    instructions: Optional[str] = None
    characteristics: Optional[Dict[str, CharacteristicValue]] = None
    price: int
    flavour: str
    weight: int

    model_config = {"from_attributes": True}


class ImageItem(BaseModel):
    key: str
    cdn_url: str = ""


class ProductWithImages(Product):
    images: List[ImageItem] = []


class Delete(BaseModel):
    message: str
