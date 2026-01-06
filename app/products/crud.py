from sqlalchemy.orm import Session
from app.products.models import ProductModel
from app.products.schemas import CreateProduct
from fastapi import HTTPException
import uuid


def insert_new_product(db: Session, product: CreateProduct):
    db_product = ProductModel(
        id=str(uuid.uuid4()),
        **product.dict()
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_products(db: Session):
    return db.query(ProductModel).all()


def get_product(db: Session, product_id: str):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def update_product_attribute(db: Session, product_id: str, attribute_name: str, attribute_value):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    setattr(product, attribute_name, attribute_value)
    db.commit()
    db.refresh(product)
    return product


def delete_item(db: Session, product_id: str):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}