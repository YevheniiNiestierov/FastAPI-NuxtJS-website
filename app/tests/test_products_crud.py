"""
Unit tests for app/products/crud.py — all CRUD functions tested against the
in-memory SQLite async session provided by conftest.
"""
import pytest
from fastapi import HTTPException

from app.products import crud
from app.products.schemas import CreateProduct
from app.products.models import ProductModel


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_payload(**overrides) -> CreateProduct:
    defaults = dict(
        product_type="Мило",
        title="Тестове мило",
        description="Опис",
        instructions=None,
        price=150,
        flavour="Манго",
        weight=100,
    )
    return CreateProduct(**{**defaults, **overrides})


async def _create_product(db, **overrides) -> ProductModel:
    return await crud.insert_new_product(db, _make_payload(**overrides))


# ── insert / get ──────────────────────────────────────────────────────────────

async def test_insert_new_product(db):
    product = await _create_product(db)
    assert product.id is not None
    assert product.title == "Тестове мило"
    assert product.price == 150


async def test_get_product_by_id(db):
    created = await _create_product(db)
    fetched = await crud.get_product(db, created.id)
    assert fetched.id == created.id
    assert fetched.title == created.title


async def test_get_product_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc_info:
        await crud.get_product(db, "non-existent-id")
    assert exc_info.value.status_code == 404


async def test_get_products_empty(db):
    result = await crud.get_products(db)
    assert result == []


async def test_get_products_returns_all(db):
    await _create_product(db, title="Мило А")
    await _create_product(db, title="Мило Б")
    result = await crud.get_products(db)
    assert len(result) == 2
    titles = {p.title for p in result}
    assert titles == {"Мило А", "Мило Б"}


# ── update ────────────────────────────────────────────────────────────────────

async def test_update_product(db):
    created = await _create_product(db, price=100)
    new_payload = _make_payload(price=250, title="Оновлене мило")
    updated = await crud.update_product(db, created.id, new_payload)
    assert updated.price == 250
    assert updated.title == "Оновлене мило"


async def test_update_product_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc_info:
        await crud.update_product(db, "ghost-id", _make_payload())
    assert exc_info.value.status_code == 404


# ── delete ────────────────────────────────────────────────────────────────────

async def test_delete_product(db):
    created = await _create_product(db)
    result = await crud.delete_item(db, created.id)
    assert result == {"message": "Product deleted"}
    with pytest.raises(HTTPException) as exc:
        await crud.get_product(db, created.id)
    assert exc.value.status_code == 404


async def test_delete_product_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc_info:
        await crud.delete_item(db, "does-not-exist")
    assert exc_info.value.status_code == 404


# ── types & flavours ──────────────────────────────────────────────────────────

async def test_add_and_get_type(db):
    await crud.add_type(db, "Новий тип")
    types = await crud.get_types(db)
    assert "Новий тип" in types


async def test_add_type_duplicate_raises_400(db):
    await crud.add_type(db, "Унікальний тип")
    with pytest.raises(HTTPException) as exc_info:
        await crud.add_type(db, "Унікальний тип")
    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail


async def test_add_and_get_flavour(db):
    await crud.add_flavour(db, "Лаванда")
    flavours = await crud.get_flavours(db)
    assert "Лаванда" in flavours


async def test_add_flavour_duplicate_raises_400(db):
    await crud.add_flavour(db, "Ромашка")
    with pytest.raises(HTTPException) as exc_info:
        await crud.add_flavour(db, "Ромашка")
    assert exc_info.value.status_code == 400


async def test_get_types_empty(db):
    assert await crud.get_types(db) == []


async def test_get_flavours_empty(db):
    assert await crud.get_flavours(db) == []

