from fastapi import HTTPException
from sqlalchemy import delete as sa_delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.cart.models import CartModel, CartItemModel
from app.products.models import ProductModel


async def get_or_create_cart(db: AsyncSession, cart_id: str) -> CartModel:
    result = await db.execute(select(CartModel).where(CartModel.cart_id == cart_id))
    cart = result.scalars().first()
    if not cart:
        cart = CartModel(cart_id=cart_id, total_price=0)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
    return cart


async def add_item(db: AsyncSession, product_id: str, cart_id: str, quantity: int = 1):
    """Add item to cart or update quantity if it exists."""
    result = await db.execute(select(ProductModel).where(ProductModel.id == product_id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Product not found")

    cart = await get_or_create_cart(db, cart_id)

    result = await db.execute(
        select(CartItemModel).where(
            CartItemModel.cart_id == cart_id,
            CartItemModel.product_id == product_id,
        )
    )
    cart_item = result.scalars().first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        db.add(CartItemModel(cart_id=cart_id, product_id=product_id, quantity=quantity))

    await db.commit()
    await db.refresh(cart)
    await update_cart_total(db, cart_id)

    return {"message": "Item added to cart", "cart_id": cart_id}


async def decrease_quantity(db: AsyncSession, product_id: str, cart_id: str):
    """Decrease quantity by 1, remove item if it reaches 0."""
    result = await db.execute(
        select(CartItemModel).where(
            CartItemModel.cart_id == cart_id,
            CartItemModel.product_id == product_id,
        )
    )
    cart_item = result.scalars().first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    cart_item.quantity -= 1
    if cart_item.quantity < 1:
        await db.delete(cart_item)

    await db.commit()
    await update_cart_total(db, cart_id)

    return {"message": "Item quantity decreased"}


async def update_cart_total(db: AsyncSession, cart_id: str):
    """Recalculate and persist cart total. Uses selectinload to avoid N+1."""
    result = await db.execute(select(CartModel).where(CartModel.cart_id == cart_id))
    cart = result.scalars().first()
    if not cart:
        return

    result = await db.execute(
        select(CartItemModel)
        .where(CartItemModel.cart_id == cart_id)
        .options(selectinload(CartItemModel.product))
    )
    items = result.scalars().all()

    cart.total_price = sum(
        float(item.product.price) * item.quantity
        for item in items if item.product
    )
    await db.commit()


async def get_products_and_total_sum(db: AsyncSession, cart_id: str):
    """Return all cart products with total sum. Uses selectinload — no N+1."""
    result = await db.execute(select(CartModel).where(CartModel.cart_id == cart_id))
    cart = result.scalars().first()
    if not cart:
        return {"products": [], "total_sum": 0}

    result = await db.execute(
        select(CartItemModel)
        .where(CartItemModel.cart_id == cart_id)
        .order_by(CartItemModel.id)
        .options(selectinload(CartItemModel.product))
    )
    items = result.scalars().all()

    products = [
        {
            "id": item.product.id,
            "title": item.product.title,
            "price": str(item.product.price),
            "quantity": item.quantity,
        }
        for item in items if item.product
    ]

    return {"products": products, "total_sum": cart.total_price}


async def clear_cart(db: AsyncSession, cart_id: str):
    """Remove all items and reset total."""
    result = await db.execute(select(CartModel).where(CartModel.cart_id == cart_id))
    cart = result.scalars().first()
    if not cart:
        return

    await db.execute(sa_delete(CartItemModel).where(CartItemModel.cart_id == cart_id))
    cart.total_price = 0
    await db.commit()
