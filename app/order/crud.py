import asyncio
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cart.crud import get_products_and_total_sum, clear_cart
from app.order.schemas import CreateOrder
from app.order.models import Order
from app.bot import send_message


async def preview_order(db: AsyncSession, session_id: str, order: CreateOrder):
    """Preview order details without creating it."""
    cart_data = await get_products_and_total_sum(db, str(session_id))
    products = cart_data["products"]
    if not products:
        raise HTTPException(status_code=400, detail="Cart is empty")

    return {
        "name": order.name,
        "delivery_type": order.delivery_type,
        "city": order.city,
        "department_number": order.department_number,
        "phone_number": order.phone_number,
        "products": products,
        "total_sum": cart_data["total_sum"],
    }


async def create_order_from_cart(db: AsyncSession, session_id: str, order: CreateOrder):
    """Create order from cart contents, then clear the cart."""
    cart_data = await get_products_and_total_sum(db, str(session_id))
    products = cart_data["products"]
    total_sum = cart_data["total_sum"]

    if not products:
        raise HTTPException(status_code=400, detail="Cart is empty")

    new_order = Order(
        order_id=str(uuid.uuid4()),
        name=order.name,
        delivery_type=order.delivery_type,
        city=order.city,
        department_number=order.department_number,
        phone_number=order.phone_number,
        products=products,
        created_at=datetime.now(timezone.utc),
        total_sum=int(total_sum),
        user_id=str(session_id),
    )

    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)

    # Telegram notification — send_message is sync, run in thread pool
    await asyncio.to_thread(send_message, dict(new_order.__dict__))

    await clear_cart(db, str(session_id))

    return {"message": "Order created successfully", "order_id": new_order.order_id}


async def get_order(db: AsyncSession, order_id: str):
    result = await db.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


async def delete_order(db: AsyncSession, order_id: str):
    result = await db.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    await db.delete(order)
    await db.commit()
    return {"message": "Order deleted successfully"}


async def _update_order_item(db: AsyncSession, order: Order, updated_products: list):
    """Persist a new product list + recalculated total on an existing order."""
    total_sum = sum(int(p["price"]) * p["quantity"] for p in updated_products)
    order.products = updated_products
    order.total_sum = total_sum
    await db.commit()
    await db.refresh(order)


async def delete_product(db: AsyncSession, order_id: str, product_id: str):
    result = await db.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    updated = [p for p in order.products if p["id"] != product_id]
    await _update_order_item(db, order, updated)


async def decrease_quantity(db: AsyncSession, order_id: str, product_id: str):
    result = await db.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Build a new list (never mutate while iterating)
    updated = []
    for p in order.products:
        if p["id"] == product_id:
            new_qty = p["quantity"] - 1
            if new_qty >= 1:
                updated.append({**p, "quantity": new_qty})
        else:
            updated.append(p)

    await _update_order_item(db, order, updated)
