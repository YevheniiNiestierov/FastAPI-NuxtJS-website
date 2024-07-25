from fastapi import Depends
from app.dynamo_db.dynamodb_config import ddb
from fastapi import Request
from starlette.responses import JSONResponse
import uuid

from app.products.crud import get_product

cart_table = ddb.Table('Carts')


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


def update_cart_item(cart_id: str, updated_products: list):
    total_sum = sum(int(product['price']) * product['quantity'] for product in updated_products)

    # Update the cart item in DynamoDB
    cart_table.put_item(
        Item={
            'cart_id': cart_id,
            'products': updated_products,
            'total_sum': total_sum,
        }
    )


def add_item(product_id: str,
             cart_id: str = Depends(get_session_id),
             quantity: int = 1
             ):

    # Get existing cart items, if any
    existing_items = cart_table.get_item(Key={'cart_id': cart_id}).get('Item', {})  # Handle case where cart doesn't exist
    products = existing_items.get('products', [])  # Initialize as empty list

    # Combine or create product information
    product = get_product(product_id)
    if products:  # Existing cart items found
        found = False
        for item in products:
            if item['id'] == product['product_id']:
                item['quantity'] += quantity  # Update quantity for existing product
                found = True
                break
        if not found:
            products.append({'id': product['product_id'], 'title': product['title'], 'price': str(product['price']), 'quantity': quantity})  # Add new product
    else:  # No existing cart items
        products = [{'id': product['product_id'], 'title': product['title'], 'price': str(product['price']), 'quantity': quantity}]
    # Update cart items in DynamoDB
    update_cart_item(cart_id, products)


def decrease_quantity(product_id, cart_id):
    cart_items = cart_table.get_item(Key={'cart_id': cart_id}).get('Item', {})
    products = cart_items.get('products', [])
    for product in products:
        if product['id'] == product_id:
            product['quantity'] -= 1
            if product['quantity'] < 1:
                products.remove(product)
    update_cart_item(cart_id, products)
    print(f'Product {product_id} quantity decreased from order {cart_id}')


def get_products_and_total_sum(session_id):
    response = cart_table.get_item(Key={'cart_id': str(session_id)})
    if 'Item' in response:
        return [response['Item'].get('products'), response['Item'].get('total_sum')]
    return []

