# python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/soap_db"
)


def _to_async_url(url: str) -> str:
    """Derive the correct async-driver URL from a sync DB URL.

    Handles both PostgreSQL (psycopg2 → asyncpg) and SQLite (→ aiosqlite)
    so that test suites can point DATABASE_URL at a file-based SQLite DB
    without installing psycopg2 locally.
    """
    if url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("sqlite://") and "+aiosqlite" not in url:
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return url  # already has the right driver prefix (e.g. sqlite+aiosqlite://)


ASYNC_DATABASE_URL = _to_async_url(DATABASE_URL)

# --- Sync engine (kept for legacy routes and one-shot utilities) ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Async engine (used by the refactored async routes) ---
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

Base = declarative_base()


def get_db():
    """Sync DB dependency — kept for routes not yet migrated to async."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """Async DB dependency for all new async route handlers."""
    async with AsyncSessionLocal() as session:
        yield session


print(f"[database] Using DB URL: {engine.url}")
