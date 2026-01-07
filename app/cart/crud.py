from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.products.crud import get_product
from app.cart.models import CartModel, CartItemModel
from app.products.models import ProductModel
import uuid


def get_or_create_cart(db: Session, cart_id: str) -> CartModel:
    """Get existing cart or create a new one"""
    cart = db.query(CartModel).filter(CartModel.cart_id == cart_id).first()
    if not cart:
        cart = CartModel(cart_id=cart_id, total_price=0)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def add_item(db: Session, product_id: str, cart_id: str, quantity: int = 1):
    """Add item to cart or update quantity if it exists"""
    # Validate product exists
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()  # or ProductModel.product_id
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get or create cart
    cart = get_or_create_cart(db, cart_id)

    # Check if product already in cart
    cart_item = db.query(CartItemModel).filter(
        CartItemModel.cart_id == cart_id,
        CartItemModel.product_id == product_id
    ).first()

    if cart_item:
        # Update quantity
        cart_item.quantity += quantity
    else:
        # Add new item
        cart_item = CartItemModel(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart)

    # Update total price
    update_cart_total(db, cart_id)

    return {"message": "Item added to cart", "cart_id": cart_id}


def decrease_quantity(db: Session, product_id: str, cart_id: str):
    """Decrease quantity by 1 or remove item if quantity becomes 0"""
    cart_item = db.query(CartItemModel).filter(
        CartItemModel.cart_id == cart_id,
        CartItemModel.product_id == product_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    cart_item.quantity -= 1

    if cart_item.quantity < 1:
        db.delete(cart_item)

    db.commit()

    # Update total price
    update_cart_total(db, cart_id)

    return {"message": "Item quantity decreased"}


def update_cart_total(db: Session, cart_id: str):
    """Recalculate and update cart total price"""
    cart = db.query(CartModel).filter(CartModel.cart_id == cart_id).first()
    if not cart:
        return

    cart_items = db.query(CartItemModel).filter(CartItemModel.cart_id == cart_id).all()

    total = 0
    for item in cart_items:
        product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
        if product:
            total += float(product.price) * item.quantity

    cart.total_price = total
    db.commit()


def get_products_and_total_sum(db: Session, cart_id: str):
    """Get all products in cart with total sum"""
    cart = db.query(CartModel).filter(CartModel.cart_id == cart_id).first()
    if not cart:
        return {"products": [], "total_sum": 0}

    cart_items = db.query(CartItemModel).filter(CartItemModel.cart_id == cart_id).all()

    products = []
    for item in cart_items:
        product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
        if product:
            products.append({
                "id": product.id,
                "title": product.title,
                "price": str(product.price),
                "quantity": item.quantity
            })

    return {"products": products, "total_sum": cart.total_price}


def clear_cart(db: Session, cart_id: str):
    """Remove all items from cart and reset total"""
    cart = db.query(CartModel).filter(CartModel.cart_id == cart_id).first()
    if not cart:
        return

    # Delete all cart items
    db.query(CartItemModel).filter(CartItemModel.cart_id == cart_id).delete()

    # Reset total price
    cart.total_price = 0
    db.commit()

