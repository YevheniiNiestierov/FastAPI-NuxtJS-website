import os
import re
import uuid
from urllib.parse import quote

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.products.models import ProductModel, ProductTypeModel, ProductFlavourModel
from app.products.schemas import CreateProduct, ImageItem
from app.s3.s3_config import s3, AWS_S3_BUCKET_NAME

# Optional CDN in front of the bucket (e.g. https://assets.example.com). When empty,
# cdn_url is left blank and the frontend serves images through the API instead.
CDN_BASE = os.environ.get("CDN_BASE", "").rstrip("/")


def fetch_all_gallery() -> dict[str, list[ImageItem]]:
    """One S3 listing for the whole bucket, grouped by product title and sorted by index."""
    contents = []
    try:
        for page in s3.get_paginator("list_objects_v2").paginate(Bucket=AWS_S3_BUCKET_NAME):
            contents.extend(page.get("Contents", []))
    except Exception:
        return {}

    grouped: dict[str, list[tuple[int, str, str, int]]] = {}
    for obj in contents:
        full_key = obj["Key"]
        base = os.path.splitext(full_key)[0]
        match = re.match(r"^(.+)_(\d+)$", base)
        name, order = (match.group(1), int(match.group(2))) if match else (base, 0)
        grouped.setdefault(name, []).append((order, base, full_key, int(obj["LastModified"].timestamp())))

    return {
        name: [
            # ?v=<last-modified> makes the URL change whenever the image is replaced/reordered,
            # which is what lets the Cloudflare Worker cache it for a year (immutable).
            ImageItem(
                key=base,
                cdn_url=f"{CDN_BASE}/{quote(full_key, safe='')}?v={version}" if CDN_BASE else "",
            )
            for _, base, full_key, version in sorted(items)
        ]
        for name, items in grouped.items()
    }

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

_DEFAULT_TYPES = [
    "Мило", "Мило для рук", "Скраб", "Мило для душу",
    "Бомбочка для вани", "Твердий шампунь", "Подарунковий набір",
]
_DEFAULT_FLAVOURS = ["Манго", "Кастильське", "Авокадо", "Чорний кмин"]


def seed_types_and_flavours(db: Session):
    """Seed default types/flavours if the tables are empty (called once at startup)."""
    if db.query(ProductTypeModel).count() == 0:
        for name in _DEFAULT_TYPES:
            db.add(ProductTypeModel(name=name))
    if db.query(ProductFlavourModel).count() == 0:
        for name in _DEFAULT_FLAVOURS:
            db.add(ProductFlavourModel(name=name))
    db.commit()


# ---------------------------------------------------------------------------
# Types / flavours
# ---------------------------------------------------------------------------

def get_types(db: Session) -> list[str]:
    rows = db.query(ProductTypeModel).order_by(ProductTypeModel.id).all()
    return [row.name for row in rows]


def get_flavours(db: Session) -> list[str]:
    rows = db.query(ProductFlavourModel).order_by(ProductFlavourModel.id).all()
    return [row.name for row in rows]


def add_type(db: Session, name: str) -> str:
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name must not be empty")
    if db.query(ProductTypeModel).filter(ProductTypeModel.name == name).first():
        raise HTTPException(status_code=400, detail="Type already exists")
    db.add(ProductTypeModel(name=name))
    db.commit()
    return name


def add_flavour(db: Session, name: str) -> str:
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name must not be empty")
    if db.query(ProductFlavourModel).filter(ProductFlavourModel.name == name).first():
        raise HTTPException(status_code=400, detail="Flavour already exists")
    db.add(ProductFlavourModel(name=name))
    db.commit()
    return name


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

def insert_new_product(db: Session, product: CreateProduct) -> ProductModel:
    db_product = ProductModel(id=str(uuid.uuid4()), **product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_products(db: Session) -> list[ProductModel]:
    return db.query(ProductModel).all()


def get_product(db: Session, product_id: str) -> ProductModel:
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def update_product(db: Session, product_id: str, product: CreateProduct) -> ProductModel:
    db_product = get_product(db, product_id)
    for key, value in product.model_dump().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_item(db: Session, product_id: str) -> dict:
    from app.cart.models import CartItemModel

    product = get_product(db, product_id)
    db.query(CartItemModel).filter(CartItemModel.product_id == product_id).delete()
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}