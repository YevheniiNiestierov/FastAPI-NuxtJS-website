"""
Unit tests for app/cart/crud.py
Verifies add/remove/total mechanics, including the selectinload-based N+1 fix.
"""
import pytest
from fastapi import HTTPException

from app.cart import crud as cart_crud
from app.products import crud as product_crud
from app.products.schemas import CreateProduct


# ── helpers ───────────────────────────────────────────────────────────────────

CART_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


async def _seed_product(db, price: int = 100, title: str = "Мило") -> str:
    product = await product_crud.insert_new_product(
        db,
        CreateProduct(
            product_type="Мило", title=title, description="Опис",
            price=price, flavour="Манго", weight=90,
        ),
    )
    return product.id


# ── add item ──────────────────────────────────────────────────────────────────

async def test_add_item_creates_cart_and_item(db):
    pid = await _seed_product(db)
    result = await cart_crud.add_item(db, pid, CART_ID, quantity=2)
    assert result["cart_id"] == CART_ID

    cart_data = await cart_crud.get_products_and_total_sum(db, CART_ID)
    assert len(cart_data["products"]) == 1
    assert cart_data["products"][0]["quantity"] == 2


async def test_add_item_product_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc_info:
        await cart_crud.add_item(db, "no-such-product", CART_ID)
    assert exc_info.value.status_code == 404


async def test_add_same_item_twice_accumulates_quantity(db):
    pid = await _seed_product(db)
    await cart_crud.add_item(db, pid, CART_ID, quantity=1)
    await cart_crud.add_item(db, pid, CART_ID, quantity=3)

    cart_data = await cart_crud.get_products_and_total_sum(db, CART_ID)
    assert cart_data["products"][0]["quantity"] == 4


# ── decrease quantity ─────────────────────────────────────────────────────────

async def test_decrease_quantity_reduces_by_one(db):
    pid = await _seed_product(db)
    await cart_crud.add_item(db, pid, CART_ID, quantity=3)
    await cart_crud.decrease_quantity(db, pid, CART_ID)

    cart_data = await cart_crud.get_products_and_total_sum(db, CART_ID)
    assert cart_data["products"][0]["quantity"] == 2


async def test_decrease_quantity_removes_item_when_reaching_zero(db):
    pid = await _seed_product(db)
    await cart_crud.add_item(db, pid, CART_ID, quantity=1)
    await cart_crud.decrease_quantity(db, pid, CART_ID)

    cart_data = await cart_crud.get_products_and_total_sum(db, CART_ID)
    assert cart_data["products"] == []


async def test_decrease_quantity_item_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc_info:
        await cart_crud.decrease_quantity(db, "no-such-product", CART_ID)
    assert exc_info.value.status_code == 404


# ── total price calculation ───────────────────────────────────────────────────

async def test_cart_total_price_is_correct(db):
    pid1 = await _seed_product(db, price=100, title="Мило А")
    pid2 = await _seed_product(db, price=200, title="Мило Б")
    await cart_crud.add_item(db, pid1, CART_ID, quantity=2)  # 200
    await cart_crud.add_item(db, pid2, CART_ID, quantity=3)  # 600

    cart_data = await cart_crud.get_products_and_total_sum(db, CART_ID)
    assert cart_data["total_sum"] == pytest.approx(800.0)


async def test_get_products_empty_cart_returns_empty(db):
    result = await cart_crud.get_products_and_total_sum(db, "non-existent-cart")
    assert result == {"products": [], "total_sum": 0}


# ── clear cart ────────────────────────────────────────────────────────────────

async def test_clear_cart_removes_all_items(db):
    pid = await _seed_product(db)
    await cart_crud.add_item(db, pid, CART_ID, quantity=5)
    await cart_crud.clear_cart(db, CART_ID)

    cart_data = await cart_crud.get_products_and_total_sum(db, CART_ID)
    assert cart_data["products"] == []
    assert cart_data["total_sum"] == 0


async def test_clear_cart_nonexistent_does_not_raise(db):
    # Should silently return, not raise
    await cart_crud.clear_cart(db, "cart-that-never-existed")

