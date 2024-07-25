import json
import uuid
from fastapi import APIRouter, Request, Cookie, Header, Depends
from app.cart.router import get_session_id
from app.order.crud import insert_new_order, delete_product, decrease_quantity, get_order
from app.order.schemas import DeliveryType, CreateOrder

router = APIRouter(
    tags=["Order"],
    prefix="/order"
)


@router.get("/delivery_types/", response_model=DeliveryType)
def get_delivery_types():
    return DeliveryType()


@router.post("/create_order/")
async def create_order(order: CreateOrder, session_id: uuid.UUID = Depends(get_session_id)):
    return insert_new_order(session_id, order)


@router.get("/get_order")
async def get_existing_order(order_id):
    return get_order(order_id)


@router.get("/delete_product_from_order")
def delete_product_from_order(order_id, product_id):
    return delete_product(order_id, product_id)


@router.get("/decrease_product_quantity")
def decrease_product_quantity(order_id, product_id):
    return decrease_quantity(order_id, product_id)


