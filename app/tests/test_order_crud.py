"""
Unit tests for app/order/crud.py

Includes a REGRESSION TEST for the datetime timezone bug:
    asyncpg raises DataError when a tz-aware datetime is inserted into a
    TIMESTAMP WITHOUT TIME ZONE column.  The fix:
        datetime.now(timezone.utc).replace(tzinfo=None)
    This test asserts that created_at is ALWAYS stored as a naive datetime,
    so the bug cannot silently reappear after a future refactor.
"""
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.cart import crud as cart_crud
from app.order import crud as order_crud
from app.order.schemas import CreateOrder
from app.products import crud as product_crud
from app.products.schemas import CreateProduct


# ── helpers ───────────────────────────────────────────────────────────────────

SESSION_ID = "11111111-2222-3333-4444-555555555555"


async def _seed_product(db, price: int = 130) -> str:
    p = await product_crud.insert_new_product(
        db,
        CreateProduct(
            product_type="Мило", title="Мило для тесту", description="Опис",
            price=price, flavour="Манго", weight=90,
        ),
    )
    return p.id


def _order_payload(**overrides) -> CreateOrder:
    defaults = dict(
        name="Тест Тестенко",
        delivery_type="Нова Пошта",
        city="Київ",
        department_number="1",
        phone_number="+380991234567",
    )
    return CreateOrder(**{**defaults, **overrides})


async def _fill_cart(db, price: int = 130, quantity: int = 2) -> str:
    pid = await _seed_product(db, price=price)
    await cart_crud.add_item(db, pid, SESSION_ID, quantity=quantity)
    return pid


# ── regression: datetime timezone ─────────────────────────────────────────────

async def test_create_order_created_at_is_naive(db):
    """
    REGRESSION TEST — asyncpg DataError:
        "can't subtract offset-naive and offset-aware datetimes"

    asyncpg refuses to insert a tz-aware datetime into a
    TIMESTAMP WITHOUT TIME ZONE column.  created_at must be a naive datetime.

    If this test fails, someone changed the timestamp creation back to
    datetime.now(timezone.utc) WITHOUT the .replace(tzinfo=None) strip.
    """
    await _fill_cart(db)

    with patch("app.order.crud.send_message"):          # suppress Telegram call
        result = await order_crud.create_order_from_cart(db, SESSION_ID, _order_payload())

    order = await order_crud.get_order(db, result["order_id"])

    assert order.created_at.tzinfo is None, (
        "created_at must be a naive (offset-free) datetime.\n"
        "asyncpg raises DataError when a tz-aware datetime is passed to a "
        "TIMESTAMP WITHOUT TIME ZONE column.\n"
        "Fix: datetime.now(timezone.utc).replace(tzinfo=None)"
    )


# ── create order ──────────────────────────────────────────────────────────────

async def test_create_order_from_cart_success(db):
    await _fill_cart(db, price=100, quantity=3)

    with patch("app.order.crud.send_message"):
        result = await order_crud.create_order_from_cart(db, SESSION_ID, _order_payload())

    assert "order_id" in result
    assert result["message"] == "Order created successfully"


async def test_create_order_clears_cart(db):
    await _fill_cart(db)

    with patch("app.order.crud.send_message"):
        await order_crud.create_order_from_cart(db, SESSION_ID, _order_payload())

    cart_data = await cart_crud.get_products_and_total_sum(db, SESSION_ID)
    assert cart_data["products"] == []


async def test_create_order_total_sum_is_correct(db):
    await _fill_cart(db, price=130, quantity=5)   # 650

    with patch("app.order.crud.send_message"):
        result = await order_crud.create_order_from_cart(db, SESSION_ID, _order_payload())

    order = await order_crud.get_order(db, result["order_id"])
    assert order.total_sum == 650


async def test_create_order_empty_cart_raises_400(db):
    with pytest.raises(HTTPException) as exc_info:
        with patch("app.order.crud.send_message"):
            await order_crud.create_order_from_cart(db, SESSION_ID, _order_payload())
    assert exc_info.value.status_code == 400
    assert "Cart is empty" in exc_info.value.detail


# ── preview order ─────────────────────────────────────────────────────────────

async def test_preview_order_returns_correct_data(db):
    await _fill_cart(db, price=100, quantity=2)
    preview = await order_crud.preview_order(db, SESSION_ID, _order_payload())

    assert preview["name"] == "Тест Тестенко"
    assert preview["total_sum"] == pytest.approx(200.0)
    assert len(preview["products"]) == 1


async def test_preview_order_empty_cart_raises_400(db):
    with pytest.raises(HTTPException) as exc_info:
        await order_crud.preview_order(db, SESSION_ID, _order_payload())
    assert exc_info.value.status_code == 400


# ── get / delete / modify order ───────────────────────────────────────────────

async def test_get_order_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc_info:
        await order_crud.get_order(db, "ghost-order-id")
    assert exc_info.value.status_code == 404


async def test_delete_product_from_order(db):
    pid = await _fill_cart(db)
    await _fill_cart(db, price=200)          # second product in same cart

    # Add a second, different product to cart
    pid2 = await _seed_product(db, price=200)
    await cart_crud.add_item(db, pid2, SESSION_ID, quantity=1)

    with patch("app.order.crud.send_message"):
        result = await order_crud.create_order_from_cart(db, SESSION_ID, _order_payload())

    order_id = result["order_id"]
    order = await order_crud.get_order(db, order_id)
    initial_count = len(order.products)

    await order_crud.delete_product(db, order_id, order.products[0]["id"])
    order = await order_crud.get_order(db, order_id)
    assert len(order.products) == initial_count - 1


async def test_decrease_order_quantity(db):
    await _fill_cart(db, quantity=3)

    with patch("app.order.crud.send_message"):
        result = await order_crud.create_order_from_cart(db, SESSION_ID, _order_payload())

    order_id = result["order_id"]
    order = await order_crud.get_order(db, order_id)
    product_id = order.products[0]["id"]

    await order_crud.decrease_quantity(db, order_id, product_id)
    order = await order_crud.get_order(db, order_id)
    assert order.products[0]["quantity"] == 2


async def test_decrease_order_quantity_removes_when_zero(db):
    await _fill_cart(db, quantity=1)

    with patch("app.order.crud.send_message"):
        result = await order_crud.create_order_from_cart(db, SESSION_ID, _order_payload())

    order_id = result["order_id"]
    order = await order_crud.get_order(db, order_id)
    product_id = order.products[0]["id"]

    await order_crud.decrease_quantity(db, order_id, product_id)
    order = await order_crud.get_order(db, order_id)
    assert order.products == []
    assert order.total_sum == 0

