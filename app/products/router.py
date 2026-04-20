from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.postgress.database import get_db
from app.products import crud
from app.products.schemas import CreateProduct, CreateProductType, CreateProductFlavour, ProductFlavour, ProductType, Product, Delete
from app.auth.jwt import get_current_admin

router = APIRouter(
    tags=["Products"],
    prefix="/product"
)


@router.on_event("startup")
def seed_on_startup():
    from app.postgress.database import SessionLocal
    db = SessionLocal()
    try:
        crud.seed_types_and_flavours(db)
    finally:
        db.close()


@router.get("/flavours/", response_model=ProductFlavour)
def get_flavours(db: Session = Depends(get_db)):
    return ProductFlavour(flavours=crud.get_flavours(db))


@router.get("/types/", response_model=ProductType)
def get_types(db: Session = Depends(get_db)):
    return ProductType(types=crud.get_types(db))


@router.post("/types/", response_model=ProductType)
def create_type(body: CreateProductType, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    crud.add_type(db, body.name.strip())
    return ProductType(types=crud.get_types(db))


@router.post("/flavours/", response_model=ProductFlavour)
def create_flavour(body: CreateProductFlavour, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    crud.add_flavour(db, body.name.strip())
    return ProductFlavour(flavours=crud.get_flavours(db))


@router.post("/create_product/", response_model=Product)
def create_product(product: CreateProduct, db: Session = Depends(get_db), current_user = Depends(get_current_admin)):
    return crud.insert_new_product(db, product)


@router.get("/products/{product_id}", response_model=Product)
def get_product_by_id(product_id: str, db: Session = Depends(get_db)):
    return crud.get_product(db, product_id)


@router.get("/products", response_model=List[Product])
def get_all_products(db: Session = Depends(get_db)):
    return crud.get_products(db)


@router.put("/products/{product_id}", response_model=Product)
def update_product(product_id: str, product: CreateProduct, db: Session = Depends(get_db), current_user = Depends(get_current_admin)):
    return crud.update_product(db, product_id, product)


@router.delete("/products/{product_id}", response_model=Delete)
def delete_by_id(product_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_admin)):
    return crud.delete_item(db, product_id)
