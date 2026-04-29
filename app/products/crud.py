import asyncio
import os
import re
import uuid
from urllib.parse import quote

from fastapi import HTTPException
from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.products.models import ProductModel, ProductTypeModel, ProductFlavourModel
from app.products.schemas import CreateProduct, ImageItem
from app.s3.s3_config import s3, AWS_S3_BUCKET_NAME, CDN_OR_S3_BASE

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

_DEFAULT_TYPES = [
    "Мило", "Мило для рук", "Скраб", "Мило для душу",
    "Бомбочка для вани", "Твердий шампунь", "Подарунковий набір",
]
_DEFAULT_FLAVOURS = ["Манго", "Кастильське", "Авокадо", "Чорний кмин"]


def seed_types_and_flavours(db: Session):
    """Seed default types/flavours if tables are empty (sync — called once at startup)."""
    if db.query(ProductTypeModel).count() == 0:
        for name in _DEFAULT_TYPES:
            db.add(ProductTypeModel(name=name))
    if db.query(ProductFlavourModel).count() == 0:
        for name in _DEFAULT_FLAVOURS:
            db.add(ProductFlavourModel(name=name))
    db.commit()


# ---------------------------------------------------------------------------
# S3 gallery helpers (boto3 is sync → wrap with asyncio.to_thread)
# ---------------------------------------------------------------------------

async def fetch_all_gallery() -> dict[str, list[ImageItem]]:
    """
    Single S3 list_objects_v2 call that fetches ALL bucket objects, then groups
    them by product title.  Returns { title: [ImageItem, ...] } sorted by index.

    This replaces the per-product gallery calls that caused the N+1 problem.
    """
    def _list() -> list:
        paginator = s3.get_paginator("list_objects_v2")
        contents: list = []
        for page in paginator.paginate(Bucket=AWS_S3_BUCKET_NAME):
            contents.extend(page.get("Contents", []))
        return contents

    contents = await asyncio.to_thread(_list)

    gallery: dict[str, list[dict]] = {}
    for obj in contents:
        full_key = obj["Key"]                         # e.g. "Мило_1.webp"
        base_key = os.path.splitext(full_key)[0]      # e.g. "Мило_1"
        match = re.match(r"^(.+)_(\d+)$", base_key)
        if not match:
            continue
        product_name = match.group(1)
        order = int(match.group(2))
        encoded_key = quote(full_key, safe="")
        cdn_url = f"{CDN_OR_S3_BASE}/{encoded_key}"
        gallery.setdefault(product_name, []).append(
            {"key": base_key, "cdn_url": cdn_url, "order": order}
        )

    # Sort each product's list by numeric suffix and convert to schema objects
    return {
        name: [
            ImageItem(key=img["key"], cdn_url=img["cdn_url"])
            for img in sorted(imgs, key=lambda x: x["order"])
        ]
        for name, imgs in gallery.items()
    }


async def fetch_product_gallery(product_title: str) -> list[ImageItem]:
    """Single-product gallery fetch (used by the detail endpoint)."""
    def _list():
        return s3.list_objects_v2(
            Bucket=AWS_S3_BUCKET_NAME, Prefix=product_title
        ).get("Contents", [])

    contents = await asyncio.to_thread(_list)
    items = []
    for obj in contents:
        full_key = obj["Key"]
        base_key = os.path.splitext(full_key)[0]
        match = re.match(r"^(.+)_(\d+)$", base_key)
        order = int(match.group(2)) if match else 0
        encoded_key = quote(full_key, safe="")
        cdn_url = f"{CDN_OR_S3_BASE}/{encoded_key}"
        items.append({"key": base_key, "cdn_url": cdn_url, "order": order})
    items.sort(key=lambda x: x["order"])
    return [ImageItem(key=i["key"], cdn_url=i["cdn_url"]) for i in items]


# ---------------------------------------------------------------------------
# Async CRUD — SQLAlchemy 2.0 select() style
# ---------------------------------------------------------------------------

async def get_types(db: AsyncSession) -> list[str]:
    result = await db.execute(select(ProductTypeModel).order_by(ProductTypeModel.id))
    return [row.name for row in result.scalars().all()]


async def get_flavours(db: AsyncSession) -> list[str]:
    result = await db.execute(select(ProductFlavourModel).order_by(ProductFlavourModel.id))
    return [row.name for row in result.scalars().all()]


async def add_type(db: AsyncSession, name: str) -> str:
    existing = (await db.execute(
        select(ProductTypeModel).where(ProductTypeModel.name == name)
    )).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Type already exists")
    db.add(ProductTypeModel(name=name))
    await db.commit()
    return name


async def add_flavour(db: AsyncSession, name: str) -> str:
    existing = (await db.execute(
        select(ProductFlavourModel).where(ProductFlavourModel.name == name)
    )).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Flavour already exists")
    db.add(ProductFlavourModel(name=name))
    await db.commit()
    return name


async def insert_new_product(db: AsyncSession, product: CreateProduct) -> ProductModel:
    db_product = ProductModel(id=str(uuid.uuid4()), **product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def get_products(db: AsyncSession) -> list[ProductModel]:
    result = await db.execute(select(ProductModel))
    return result.scalars().all()


async def get_product(db: AsyncSession, product_id: str) -> ProductModel:
    result = await db.execute(
        select(ProductModel).where(ProductModel.id == product_id)
    )
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


async def update_product(
    db: AsyncSession, product_id: str, product: CreateProduct
) -> ProductModel:
    result = await db.execute(
        select(ProductModel).where(ProductModel.id == product_id)
    )
    db_product = result.scalars().first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.model_dump().items():
        setattr(db_product, key, value)
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def delete_item(db: AsyncSession, product_id: str) -> dict:
    from app.cart.models import CartItemModel

    result = await db.execute(
        select(ProductModel).where(ProductModel.id == product_id)
    )
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.execute(
        sa_delete(CartItemModel).where(CartItemModel.product_id == product_id)
    )
    await db.delete(product)
    await db.commit()
    return {"message": "Product deleted"}