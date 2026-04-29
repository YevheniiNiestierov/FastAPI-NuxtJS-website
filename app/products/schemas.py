from typing import List

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


class ImageItem(BaseModel):
    """A single gallery image: S3 base key + its ready-to-use Cloudflare CDN URL."""
    key: str
    cdn_url: str


class ProductWithImages(Product):
    """Product enriched with its pre-fetched CDN gallery. Eliminates N+1 on the frontend."""
    images: List[ImageItem] = []


class Delete(BaseModel):
    message: str

