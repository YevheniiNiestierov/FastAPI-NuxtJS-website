import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.sqlite.database import Base, engine
from app.products import router as product_router
from app.users import router as user_router
from app.cart import router as cart_router
from app.order import router as order_router
from app.images import router as image_router
from app.auth import router as auth_router

app = FastAPI()

origins = [
    "https://natur-savon.com.ua",
    "http://natur-savon.com.ua",
    "http://localhost:3000",
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

Base.metadata.create_all(bind=engine)


@app.get("/home")
def say_hi():
    return "Hi!"


if __name__ == '__main__':
    uvicorn.run(app, host="localhost", port=8001, reload=False)

