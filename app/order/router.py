from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.cart.router import get_session_id
from app.order.crud import (
    create_order_from_cart, preview_order,
    delete_product, decrease_quantity, get_order,
)
from app.order.schemas import DeliveryType, CreateOrder
from app.postgress.database import get_async_db

router = APIRouter(
    tags=["Order"],
    prefix="/order",
)


@router.get("/delivery_types/", response_model=DeliveryType)
def get_delivery_types():
    return DeliveryType()


@router.post("/create_order/")
async def create_order(
    order: CreateOrder,
    session_id: str = Depends(get_session_id),
    db: AsyncSession = Depends(get_async_db),
):
    return await create_order_from_cart(db, session_id, order)


@router.post("/preview_order/")
async def preview_order_details(
    order: CreateOrder,
    session_id: str = Depends(get_session_id),
    db: AsyncSession = Depends(get_async_db),
):
    return await preview_order(db, session_id, order)


@router.get("/get_order")
async def get_existing_order(order_id: str, db: AsyncSession = Depends(get_async_db)):
    return await get_order(db, order_id)


@router.get("/delete_product_from_order")
async def delete_product_from_order(
    order_id: str,
    product_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    return await delete_product(db, order_id, product_id)


@router.get("/decrease_product_quantity")
async def decrease_product_quantity(
    order_id: str,
    product_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    return await decrease_quantity(db, order_id, product_id)
