# python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/soap_db"
)

# Derive the asyncpg URL from the sync URL (handles both plain and driver-qualified URLs)
ASYNC_DATABASE_URL = (
    DATABASE_URL
    .replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    .replace("postgresql://", "postgresql+asyncpg://", 1)
)

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
