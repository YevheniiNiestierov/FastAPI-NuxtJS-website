from sqlalchemy.orm import Session
from app.products.models import ProductModel, ProductTypeModel, ProductFlavourModel
from app.products.schemas import CreateProduct
from fastapi import HTTPException
import uuid

# Default seed data
_DEFAULT_TYPES = ["Мило", "Мило для рук", "Скраб", "Мило для душу", "Бомбочка для вани", "Твердий шампунь", "Подарунковий набір"]
_DEFAULT_FLAVOURS = ["Манго", "Кастильське", "Авокадо", "Чорний кмин"]


def seed_types_and_flavours(db: Session):
    """Seed default types/flavours if tables are empty."""
    if db.query(ProductTypeModel).count() == 0:
        for name in _DEFAULT_TYPES:
            db.add(ProductTypeModel(name=name))
    if db.query(ProductFlavourModel).count() == 0:
        for name in _DEFAULT_FLAVOURS:
            db.add(ProductFlavourModel(name=name))
    db.commit()


def get_types(db: Session):
    return [row.name for row in db.query(ProductTypeModel).order_by(ProductTypeModel.id).all()]


def get_flavours(db: Session):
    return [row.name for row in db.query(ProductFlavourModel).order_by(ProductFlavourModel.id).all()]


def add_type(db: Session, name: str):
    existing = db.query(ProductTypeModel).filter(ProductTypeModel.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Type already exists")
    obj = ProductTypeModel(name=name)
    db.add(obj)
    db.commit()
    return name


def add_flavour(db: Session, name: str):
    existing = db.query(ProductFlavourModel).filter(ProductFlavourModel.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Flavour already exists")
    obj = ProductFlavourModel(name=name)
    db.add(obj)
    db.commit()
    return name


# ...existing code...


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


def update_product(db: Session, product_id: str, product: CreateProduct):
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_item(db: Session, product_id: str):
    from app.cart.models import CartItemModel
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.query(CartItemModel).filter(CartItemModel.product_id == product_id).delete()
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}