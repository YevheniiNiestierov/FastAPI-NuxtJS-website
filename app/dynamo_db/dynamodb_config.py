import boto3
import os


AWS_ACCESS_KEY_ID = os.environ['AWS_DYNAMODB_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_DYNAMODB_SECRET_ACCESS_KEY']
AWS_REGION_NAME = os.environ['AWS_DYNAMODB_REGION_NAME']

ddb = boto3.resource('dynamodb',
                         region_name=AWS_REGION_NAME,
                         aws_access_key_id=AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY)



