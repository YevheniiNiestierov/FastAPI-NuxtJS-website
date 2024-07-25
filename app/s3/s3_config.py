import boto3
import os


AWS_ACCESS_KEY_ID = os.environ['AWS_S3_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_S3_SECRET_ACCESS_KEY']
AWS_REGION_NAME = os.environ['AWS_S3_REGION_NAME']
AWS_S3_BUCKET_NAME = 'natur-savon-images'


s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME
)

bucket_name = AWS_S3_BUCKET_NAME


