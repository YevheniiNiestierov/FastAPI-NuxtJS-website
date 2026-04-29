from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.postgress.database import get_async_db
from app.products import crud
from app.products.schemas import (
    CreateProduct, CreateProductType, CreateProductFlavour,
    ProductFlavour, ProductType, Product, ProductWithImages, ImageItem, Delete,
)
from app.auth.jwt import get_current_admin

router = APIRouter(
    tags=["Products"],
    prefix="/product",
)


@router.get("/flavours/", response_model=ProductFlavour)
async def get_flavours(db: AsyncSession = Depends(get_async_db)):
    return ProductFlavour(flavours=await crud.get_flavours(db))


@router.get("/types/", response_model=ProductType)
async def get_types(db: AsyncSession = Depends(get_async_db)):
    return ProductType(types=await crud.get_types(db))


@router.post("/types/", response_model=ProductType)
async def create_type(
    body: CreateProductType,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_admin),
):
    await crud.add_type(db, body.name.strip())
    return ProductType(types=await crud.get_types(db))


@router.post("/flavours/", response_model=ProductFlavour)
async def create_flavour(
    body: CreateProductFlavour,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_admin),
):
    await crud.add_flavour(db, body.name.strip())
    return ProductFlavour(flavours=await crud.get_flavours(db))


@router.post("/create_product/", response_model=Product)
async def create_product(
    product: CreateProduct,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_admin),
):
    return await crud.insert_new_product(db, product)


@router.get("/products/{product_id}", response_model=ProductWithImages)
async def get_product_by_id(
    product_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    product = await crud.get_product(db, product_id)
    images = await crud.fetch_product_gallery(product.title)
    return ProductWithImages(
        id=product.id,
        product_type=product.product_type,
        title=product.title,
        description=product.description,
        instructions=product.instructions,
        price=product.price,
        flavour=product.flavour,
        weight=product.weight,
        images=images,
    )


@router.get("/products", response_model=List[ProductWithImages])
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    """
    Returns all products with their CDN image galleries embedded.
    Uses a SINGLE S3 list_objects_v2 call (via pagination) for the entire bucket,
    then distributes images to each product in Python — eliminates the N+1 problem.
    """
    products, gallery = await _fetch_products_and_gallery(db)
    result: list[ProductWithImages] = []
    for p in products:
        images = gallery.get(p.title, [])
        result.append(
            ProductWithImages(
                id=p.id,
                product_type=p.product_type,
                title=p.title,
                description=p.description,
                instructions=p.instructions,
                price=p.price,
                flavour=p.flavour,
                weight=p.weight,
                images=images,
            )
        )
    return result


async def _fetch_products_and_gallery(db: AsyncSession):
    """Run DB query and S3 listing concurrently."""
    import asyncio
    products_coro = crud.get_products(db)
    gallery_coro = crud.fetch_all_gallery()
    products, gallery = await asyncio.gather(products_coro, gallery_coro)
    return products, gallery


@router.put("/products/{product_id}", response_model=Product)
async def update_product(
    product_id: str,
    product: CreateProduct,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_admin),
):
    return await crud.update_product(db, product_id, product)


@router.delete("/products/{product_id}", response_model=Delete)
async def delete_by_id(
    product_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_admin),
):
    return await crud.delete_item(db, product_id)
