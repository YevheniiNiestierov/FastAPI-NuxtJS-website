import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.cart.router import get_session_id
from app.order.crud import insert_new_order, delete_product, decrease_quantity, get_order
from app.order.schemas import DeliveryType, CreateOrder
from app.sqlite.database import get_db

router = APIRouter(
    tags=["Order"],
    prefix="/order"
)


@router.get("/delivery_types/", response_model=DeliveryType)
def get_delivery_types():
    return DeliveryType()


@router.post("/create_order/")
async def create_order(
    order: CreateOrder,
    session_id: uuid.UUID = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    return insert_new_order(db, session_id, order)


@router.get("/get_order")
async def get_existing_order(order_id: str, db: Session = Depends(get_db)):
    return get_order(db, order_id)


@router.get("/delete_product_from_order")
def delete_product_from_order(
    order_id: str,
    product_id: str,
    db: Session = Depends(get_db)
):
    return delete_product(db, order_id, product_id)


@router.get("/decrease_product_quantity")
def decrease_product_quantity(
    order_id: str,
    product_id: str,
    db: Session = Depends(get_db)
):
    return decrease_quantity(db, order_id, product_id)
