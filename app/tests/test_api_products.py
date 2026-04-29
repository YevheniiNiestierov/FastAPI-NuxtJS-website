"""
Integration tests for the products API endpoints.
Uses the lightweight test FastAPI app from conftest (no lifespan/seeding),
httpx.AsyncClient, and mocked S3 gallery calls.
"""
from unittest.mock import patch, AsyncMock

import pytest

from app.products.schemas import CreateProduct
from app.users.models import User
from app.users.hashing import get_password_hash
from app.auth.jwt import create_access_token


# ── helpers ───────────────────────────────────────────────────────────────────

def _auth_headers(is_admin: bool = True) -> dict:
    token = create_access_token({"sub": "admin@test.com", "is_admin": is_admin})
    return {"Authorization": f"Bearer {token}"}


async def _seed_admin_user(db):
    user = User(
        username="admin",
        email="admin@test.com",
        password=get_password_hash("password"),
        role=1,
        is_admin=True,
    )
    from sqlalchemy import text
    import uuid
    user.id = str(uuid.uuid4())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


def _empty_gallery_mock():
    """Patch fetch_all_gallery to return {} (no S3 images)."""
    return patch("app.products.router.crud.fetch_all_gallery", new=AsyncMock(return_value={}))


def _product_gallery_mock():
    """Patch fetch_product_gallery to return [] for the detail endpoint."""
    return patch("app.products.router.crud.fetch_product_gallery", new=AsyncMock(return_value=[]))


# ── GET /product/products ─────────────────────────────────────────────────────

async def test_get_all_products_empty(client):
    with _empty_gallery_mock():
        response = await client.get("/product/products")
    assert response.status_code == 200
    assert response.json() == []


async def test_get_all_products_returns_embedded_images(client, db):
    await _seed_admin_user(db)
    # Create a product directly via CRUD to avoid needing admin auth complexity
    from app.products import crud
    product = await crud.insert_new_product(
        db,
        CreateProduct(
            product_type="Мило", title="Мило API тест", description="Опис",
            price=200, flavour="Манго", weight=100,
        ),
    )
    from app.products.schemas import ImageItem
    mock_gallery = {product.title: [ImageItem(key="Мило API тест_1", cdn_url="https://cdn.example.com/test.webp")]}
    with patch("app.products.router.crud.fetch_all_gallery", new=AsyncMock(return_value=mock_gallery)):
        response = await client.get("/product/products")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Мило API тест"
    assert len(data[0]["images"]) == 1
    assert data[0]["images"][0]["key"] == "Мило API тест_1"


# ── GET /product/products/{id} ────────────────────────────────────────────────

async def test_get_product_by_id_success(client, db):
    from app.products import crud
    product = await crud.insert_new_product(
        db,
        CreateProduct(
            product_type="Мило", title="Детальне мило", description="Опис",
            price=100, flavour="Манго", weight=90,
        ),
    )
    with _product_gallery_mock():
        response = await client.get(f"/product/products/{product.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(product.id)
    assert body["title"] == "Детальне мило"
    assert body["images"] == []


async def test_get_product_by_id_not_found(client):
    with _product_gallery_mock():
        response = await client.get("/product/products/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


# ── POST /product/create_product/ ────────────────────────────────────────────

async def test_create_product_requires_auth(client):
    response = await client.post("/product/create_product/", json={
        "product_type": "Мило", "title": "No auth",
        "description": "Desc", "price": 100, "flavour": "Манго", "weight": 90,
    })
    # Without auth token — should be 401 or 403
    assert response.status_code in (401, 403)


async def test_create_product_with_admin_token(client, db):
    await _seed_admin_user(db)
    payload = {
        "product_type": "Скраб",
        "title": "Новий скраб",
        "description": "Опис скрабу",
        "price": 180,
        "flavour": "Кастильське",
        "weight": 150,
    }
    response = await client.post(
        "/product/create_product/",
        json=payload,
        headers=_auth_headers(),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Новий скраб"
    assert body["price"] == 180


# ── DELETE /product/products/{id} ────────────────────────────────────────────

async def test_delete_product_with_admin_token(client, db):
    await _seed_admin_user(db)
    from app.products import crud
    product = await crud.insert_new_product(
        db,
        CreateProduct(
            product_type="Мило", title="Мило для видалення", description="Desc",
            price=100, flavour="Манго", weight=90,
        ),
    )
    response = await client.delete(
        f"/product/products/{product.id}",
        headers=_auth_headers(),
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Product deleted"


# ── GET /product/types/ & /product/flavours/ ─────────────────────────────────

async def test_get_types_empty(client):
    response = await client.get("/product/types/")
    assert response.status_code == 200
    assert response.json() == {"types": []}


async def test_get_flavours_empty(client):
    response = await client.get("/product/flavours/")
    assert response.status_code == 200
    assert response.json() == {"flavours": []}

