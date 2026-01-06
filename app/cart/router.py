from fastapi import APIRouter, Request, Depends
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from app.cart.crud import add_item, get_products_and_total_sum, decrease_quantity
from app.sqlite.database import get_db
import uuid

router = APIRouter(
    tags=["Cart"],
    prefix="/cart"
)


async def get_session_id(request: Request):
    session_id_header = request.headers.get("Session-ID")

    if not session_id_header:
        return None

    try:
        session_id = uuid.UUID(session_id_header)
        return str(session_id)
    except ValueError:
        return JSONResponse(
            content={"error": "Invalid session ID format"}, status_code=400
        )


@router.get("/add/{product_id}")
async def add_item_to_cart(
    product_id: str,
    quantity: int = 1,
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    return add_item(db, product_id, session_id, quantity)


@router.get("/delete/{product_id}")
async def delete_item_from_cart(
    product_id: str,
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    return decrease_quantity(db, product_id, session_id)


@router.get("/cart-products-and_total-price")
async def get_products_and_total_sum_in_cart(
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    return get_products_and_total_sum(db, session_id)
