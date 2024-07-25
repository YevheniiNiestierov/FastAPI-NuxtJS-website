from botocore.exceptions import ClientError
from fastapi import HTTPException

from app.cart.crud import get_products_and_total_sum
from app.dynamo_db.dynamodb_config import ddb
from datetime import datetime
import uuid

from app.order.schemas import CreateOrder

order_table = ddb.Table('Orders')


def insert_new_order(session_id: uuid.UUID, order: CreateOrder):
    products = get_products_and_total_sum(session_id)
    total_sum = 0
    current_time = datetime.utcnow().isoformat()
    for product in products:
        total_sum += int(product['price']) * product['quantity']
    # Assuming order_table is your database/table instance
    order_table.put_item(
        Item={
            'order_id': str(uuid.uuid4()),
            'name': order.name,
            'delivery_type': order.delivery_type,
            'city': order.city,
            'department_number': order.department_number,
            'phone_number': order.phone_number,
            'products': products,
            'created_at': current_time,
            'total_sum': total_sum,
            'user_id': str(session_id)
        }
    )
    return {"message": "Order created successfully"}


def get_order(order_id: str):
    response = order_table.get_item(Key={'order_id': order_id})
    return response['Item']


def delete_order(order_id):
    try:
        response = order_table.delete_item(Key={'order_id': order_id})
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return response


def update_order_item(order_id: str, updated_products: list, current_time: str, user_id: str):
    total_sum = sum(int(product['price']) * product['quantity'] for product in updated_products)

    # Update the order item in DynamoDB
    order_table.put_item(
        Item={
            'order_id': order_id,
            'products': updated_products,
            'created_at': current_time,
            'total_sum': total_sum,
            'user_id': user_id
        }
    )


def delete_product(order_id: str, product_id: str):
    response = order_table.get_item(Key={'order_id': order_id})
    if 'Item' in response:
        order_item = response['Item']
        products = order_item.get('products', [])
        updated_products = [p for p in products if p['id'] != product_id]
        update_order_item(order_id, updated_products, order_item.get('created_at'), order_item.get('user_id'))
        print(f'Product {product_id} deleted from order {order_id}')
    else:
        print(f'Order {order_id} not found')


#questionable thing, might delete later:
# def add_product_to_order(order_id: str, product_id: str):
#     response = order_table.get_item(Key={'order_id': order_id})
#     if 'Item' in response:
#         order_item = response['Item']
#         order_item.get('products', []).append(get_product(product_id))
#         products = order_item.get('products', [])
#         update_order_item(order_id, products, order_item.get('created_at'), order_item.get('user_id'))
#         print(f'Product {product_id} deleted from order {order_id}')
#     else:
#         print(f'Order {order_id} not found')


def decrease_quantity(order_id: str, product_id: str):
    response = order_table.get_item(Key={'order_id': order_id})
    if 'Item' in response:
        order_item = response['Item']
        products = order_item.get('products', [])
        for product in products:
            if product['id'] == product_id:
                product['quantity'] -= 1
                if product['quantity'] < 1:
                    products.remove(product)
        update_order_item(order_id, products, order_item.get('created_at'), order_item.get('user_id'))
        print(f'Product {product_id} quantity decreased from order {order_id}')
    else:
        print(f'Order {order_id} not found')





