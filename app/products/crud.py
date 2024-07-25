from botocore.exceptions import ClientError
from fastapi import HTTPException
from app.dynamo_db.dynamodb_config import ddb
import uuid


table = ddb.Table('Products')


def insert_new_product(product_type: str, title: str, description: str, price: int, flavour: str, weight: int):
    table.put_item(
        Item={
                'product_id': str(uuid.uuid4()),
                'product_type': product_type,
                'title': title,
                'description': description,
                'price': price,
                'flavour': flavour,
                'weight': weight
            }
        )


def get_products():
    response = table.scan()
    return response.get('Items', [])


def get_product(product_id):
    response = table.get_item(Key={'product_id': product_id})
    return response.get('Item', None)


def update_product_attribute(product_id: str, attribute_name: str, attribute_value):

    # Define the update expression to update only one attribute
    update_expression = f'SET {attribute_name} = :value'

    # Define the expression attribute values
    expression_attribute_values = {
        ':value': attribute_value
    }

    # Perform the update operation
    response = table.update_item(
        Key={
            'product_id': product_id
        },
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ReturnValues='UPDATED_NEW'  # Optional: specify what values should be returned after the update
    )

    return response


def delete_item(product_id):
    try:
        response = table.delete_item(Key={'product_id': product_id})
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return response