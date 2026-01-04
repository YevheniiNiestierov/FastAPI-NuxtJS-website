# Note: This code currently uses redis for session logic.
# I plan to rewrite the code to use DynamoDB in the future.

import json
from fastapi import APIRouter, Request, Depends
from starlette.responses import JSONResponse
from app.cart.crud import add_item, get_products_and_total_sum, decrease_quantity

import uuid
from app.redis_client.redis_connect import redis_client

router = APIRouter(
    tags=["Cart"],
    prefix="/cart"
)


async def get_session_id(request: Request):
    session_id_header = request.headers.get("Session-ID")

    if not session_id_header:
        return None  # Return None if no session ID is found in the header

    try:
        # Validate the session ID format (assuming UUID)
        session_id = uuid.UUID(session_id_header)
        return str(session_id)
    except ValueError:
        return JSONResponse(
            content={"error": "Invalid session ID format"}, status_code=400
        )


def get_cart(session_id: uuid.UUID = Depends(get_session_id)):
    cart = redis_client.get(session_id)
    # Decode existing data if it exists
    if cart:
        cart = json.loads(cart)
    else:
        # If no existing data, initialize with an empty dictionary
        cart = {"products": {}}
    return cart


#redis implementation
@router.get("/add/{product_id}")
async def add_item_to_cart(product_id: str, session_id: str = Depends(get_session_id), quantity: int = 1):
    return add_item(product_id, session_id, quantity)


@router.get("/delete/{product_id}")
async def delete_item_from_cart(product_id: str, session_id: uuid.UUID = Depends(get_session_id)):
    return decrease_quantity(product_id, str(session_id))


@router.get("/cart-products-and_total-price")
async def get_products_and_total_sum_in_cart(session_id: uuid.UUID = Depends(get_session_id)):
    return get_products_and_total_sum(str(session_id))




