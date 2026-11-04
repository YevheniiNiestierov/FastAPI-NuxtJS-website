from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.postgres.database import get_db
from app.products import crud
from app.products.schemas import (
    CreateProduct, CreateProductFlavour, CreateProductType,
    ProductFlavour, ProductType, Product, ProductWithImages, Delete,
)
from app.auth.jwt import get_current_admin

router = APIRouter(
    tags=["Products"],
    prefix="/product"
)


@router.get("/flavours/", response_model=ProductFlavour)
def get_flavours(db: Session = Depends(get_db), current_user = Depends(get_current_admin)):
    return ProductFlavour(flavours=crud.get_flavours(db))


@router.post("/flavours/", response_model=ProductFlavour)
def add_flavour(data: CreateProductFlavour, db: Session = Depends(get_db), current_user = Depends(get_current_admin)):
    crud.add_flavour(db, data.name)
    return ProductFlavour(flavours=crud.get_flavours(db))


@router.get("/types/", response_model=ProductType)
def get_types(db: Session = Depends(get_db)):
    return ProductType(types=crud.get_types(db))


@router.post("/types/", response_model=ProductType)
def add_type(data: CreateProductType, db: Session = Depends(get_db), current_user = Depends(get_current_admin)):
    crud.add_type(db, data.name)
    return ProductType(types=crud.get_types(db))


@router.post("/create_product/", response_model=Product)
def create_product(product: CreateProduct, db: Session = Depends(get_db), current_user = Depends(get_current_admin)):
    return crud.insert_new_product(db, product)


@router.get("/products/{id_or_slug}", response_model=Product)
def get_product_by_id(id_or_slug: str, db: Session = Depends(get_db)):
    return crud.get_product(db, id_or_slug)


@router.get("/products", response_model=List[ProductWithImages])
def get_all_products(db: Session = Depends(get_db)):
    gallery = crud.fetch_all_gallery()
    result = []
    for product in crud.get_products(db):
        item = ProductWithImages.model_validate(product)
        item.images = gallery.get(product.title, [])
        result.append(item)
    return result


@router.put("/products/{product_id}", response_model=Product)
def update_by_id(product_id: str, product: CreateProduct, db: Session = Depends(get_db), current_user = Depends(get_current_admin)):
    return crud.update_product(db, product_id, product)


@router.delete("/products/{product_id}", response_model=Delete)
def delete_by_id(product_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_admin)):
    return crud.delete_item(db, product_id)
