from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.cart.crud import get_products_and_total_sum, clear_cart
from app.order.schemas import CreateOrder
from app.order.models import Order

from app.bot import send_message


def preview_order(db: Session, session_id: uuid.UUID, order: CreateOrder):
    """Preview order details without creating it"""
    cart_data = get_products_and_total_sum(db, str(session_id))
    products = cart_data['products']
    total_sum = cart_data['total_sum']

    if not products:
        raise HTTPException(status_code=400, detail="Cart is empty")

    return {
        "name": order.name,
        "delivery_type": order.delivery_type,
        "city": order.city,
        "department_number": order.department_number,
        "phone_number": order.phone_number,
        "products": products,
        "total_sum": total_sum
    }


def create_order_from_cart(db: Session, session_id: uuid.UUID, order: CreateOrder):
    """Create order and clear cart"""
    cart_data = get_products_and_total_sum(db, str(session_id))
    products = cart_data['products']
    total_sum = cart_data['total_sum']

    if not products:
        raise HTTPException(status_code=400, detail="Cart is empty")

    new_order = Order(
        order_id=str(uuid.uuid4()),
        name=order.name,
        delivery_type=order.delivery_type,
        city=order.city,
        department_number=order.department_number,
        phone_number=order.phone_number,
        products=products,
        created_at=datetime.utcnow(),
        total_sum=int(total_sum),
        user_id=str(session_id)
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Notify via bot
    send_message(new_order)

    clear_cart(db, str(session_id))

    return {"message": "Order created successfully", "order_id": new_order.order_id}


def get_order(db: Session, order_id: str):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


def delete_order(db: Session, order_id: str):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully"}


def update_order_item(db: Session, order_id: str, updated_products: list):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    total_sum = sum(int(product['price']) * product['quantity'] for product in updated_products)
    order.products = updated_products
    order.total_sum = total_sum

    db.commit()
    db.refresh(order)


def delete_product(db: Session, order_id: str, product_id: str):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    updated_products = [p for p in order.products if p['id'] != product_id]
    update_order_item(db, order_id, updated_products)


def decrease_quantity(db: Session, order_id: str, product_id: str):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    products = order.products
    for product in products:
        if product['id'] == product_id:
            product['quantity'] -= 1
            if product['quantity'] < 1:
                products.remove(product)

    update_order_item(db, order_id, products)
