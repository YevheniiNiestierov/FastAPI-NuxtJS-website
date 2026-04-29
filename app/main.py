import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.postgress.database import Base, async_engine, SessionLocal
from app.products import router as product_router
from app.users import router as user_router
from app.cart import router as cart_router
from app.order import router as order_router
from app.images import router as image_router
from app.auth import router as auth_router
from app.products.crud import seed_types_and_flavours


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    # Create all tables using the async engine
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default product types / flavours (sync, runs once)
    db = SessionLocal()
    try:
        seed_types_and_flavours(db)
    finally:
        db.close()

    yield  # application runs here

    # --- Shutdown ---
    await async_engine.dispose()


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://natur-savon.com.ua",
    "https://www.natur-savon.com.ua",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product_router.router)
app.include_router(user_router.router)
app.include_router(cart_router.router)
app.include_router(order_router.router)
app.include_router(image_router.router)
app.include_router(auth_router.router)


@app.get("/home")
async def say_hi():
    return "Hi!"


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, reload=False)
