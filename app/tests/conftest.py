# conftest.py
# ── Env vars MUST be set before any app module is imported, because several
#    modules read os.environ at module level (s3_config, bot, jwt).
import os

os.environ.setdefault("AWS_S3_ACCESS_KEY_ID",     "test-key-id")
os.environ.setdefault("AWS_S3_SECRET_ACCESS_KEY",  "test-secret-key")
os.environ.setdefault("AWS_S3_REGION_NAME",        "us-east-1")
os.environ.setdefault("ASSETS_CDN_BASE_URL",       "https://test-cdn.example.com")
os.environ.setdefault("JWT_SECRET_KEY",            "test-jwt-secret-for-tests-only")
os.environ.setdefault("ADMIN_USERNAME",            "testadmin")
os.environ.setdefault("ADMIN_PASSWORD",            "testpassword123")
os.environ.setdefault("ADMIN_EMAIL",               "admin@test.com")
os.environ.setdefault("BOT_API_TOKEN",             "0000000000:test-bot-token")
os.environ.setdefault("CHAT_ID",                   "123456789")
# Point DATABASE_URL at SQLite so database.py doesn't try to import psycopg2
# (psycopg2-binary is a Docker-only dependency; tests use aiosqlite instead)
os.environ.setdefault("DATABASE_URL",              "sqlite:///./test_dummy.db")

# ── Now it is safe to import app modules ──────────────────────────────────────
import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from app.postgress.database import Base, get_async_db

# Import every model so SQLAlchemy's mapper is aware of them before create_all
from app.products.models import ProductModel, ProductTypeModel, ProductFlavourModel  # noqa: F401
from app.cart.models import CartModel, CartItemModel                                  # noqa: F401
from app.order.models import Order                                                    # noqa: F401
from app.users.models import User                                                     # noqa: F401

# ── In-memory SQLite engine (shared for the whole test session) ───────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_SessionFactory = async_sessionmaker(_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _create_tables():
    """Create all tables once per test session, drop them at the end."""
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db():
    """
    Provides a clean AsyncSession for each test.
    All rows inserted during the test are deleted afterwards so tests are
    fully isolated without needing a transaction rollback trick.
    """
    async with _SessionFactory() as session:
        yield session
        # Cleanup in FK-safe order
        await session.execute(delete(CartItemModel))
        await session.execute(delete(CartModel))
        await session.execute(delete(Order))
        await session.execute(delete(ProductModel))
        await session.execute(delete(ProductFlavourModel))
        await session.execute(delete(ProductTypeModel))
        await session.execute(delete(User))
        await session.commit()


# ── Lightweight test FastAPI app (no lifespan, no seeding) ───────────────────
def _make_test_app(session) -> FastAPI:
    """Build a minimal FastAPI app with all routers and the DB dependency overridden."""
    from app.products.router import router as product_router
    from app.cart.router    import router as cart_router
    from app.order.router   import router as order_router
    from app.auth.router    import router as auth_router
    from app.users.router   import router as user_router

    test_app = FastAPI()

    async def _override_db():
        yield session

    test_app.dependency_overrides[get_async_db] = _override_db
    test_app.include_router(product_router)
    test_app.include_router(cart_router)
    test_app.include_router(order_router)
    test_app.include_router(auth_router)
    test_app.include_router(user_router)
    return test_app


@pytest_asyncio.fixture
async def client(db):
    """httpx AsyncClient wired to the test app with the test DB session."""
    app = _make_test_app(db)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# ── Reusable data helpers ─────────────────────────────────────────────────────
@pytest.fixture
def product_payload() -> dict:
    return {
        "product_type": "Мило",
        "title": "Тестове мило",
        "description": "Опис тестового мила",
        "instructions": "Намилити, змити.",
        "price": 150,
        "flavour": "Манго",
        "weight": 100,
    }

