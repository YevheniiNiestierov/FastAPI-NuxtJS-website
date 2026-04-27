import boto3
import os


AWS_ACCESS_KEY_ID = os.environ['AWS_S3_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_S3_SECRET_ACCESS_KEY']
AWS_REGION_NAME = os.environ['AWS_S3_REGION_NAME']
AWS_S3_BUCKET_NAME = 'natur-savon-images'

# Public CDN base URL (e.g. https://assets.natur-savon.com.ua).
# Images are served directly from Cloudflare; FastAPI is not involved in delivery.
CDN_BASE_URL = os.environ.get('ASSETS_CDN_BASE_URL', '').rstrip('/')

# If CDN is not configured, fall back to the direct S3 URL so images still load.
_S3_DIRECT_BASE = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_REGION_NAME}.amazonaws.com"
CDN_OR_S3_BASE = CDN_BASE_URL or _S3_DIRECT_BASE

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME
)

bucket_name = AWS_S3_BUCKET_NAME


