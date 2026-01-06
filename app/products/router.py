from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.sqlite.database import get_db
from app.products import crud
from app.products.schemas import CreateProduct, ProductFlavour, ProductType, Product, Delete

router = APIRouter(
    tags=["Products"],
    prefix="/product"
)


@router.get("/flavours/", response_model=ProductFlavour)
def get_flavours():
    return ProductFlavour()


@router.get("/types/", response_model=ProductType)
def get_types():
    return ProductType()


@router.post("/create_product/", response_model=Product)
def create_product(product: CreateProduct, db: Session = Depends(get_db)):
    return crud.insert_new_product(db, product)


@router.get("/products/{product_id}", response_model=Product)
def get_product_by_id(product_id: str, db: Session = Depends(get_db)):
    return crud.get_product(db, product_id)


@router.get("/products", response_model=List[Product])
def get_all_products(db: Session = Depends(get_db)):
    return crud.get_products(db)


@router.delete("/products/{product_id}", response_model=Delete)
def delete_by_id(product_id: str, db: Session = Depends(get_db)):
    return crud.delete_item(db, product_id)
