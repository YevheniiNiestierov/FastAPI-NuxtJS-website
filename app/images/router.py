from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import RedirectResponse
from app.s3.s3_config import s3, AWS_S3_BUCKET_NAME
import logging
import os
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Image"],
    prefix="/image"
)


@router.get("/images/upload")
def get_upload_url(filename: str, content_type: str = "image/jpeg", expires=9999):
    allowed_types = ["image/jpeg", "image/png", "image/heic"]
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid content type. Allowed: {', '.join(allowed_types)}"
        )

    response = s3.generate_presigned_url(
        ClientMethod="put_object",
        ExpiresIn=expires,
        Params={
            "Bucket": AWS_S3_BUCKET_NAME,
            "Key": filename,
            "ContentType": content_type
        },
    )
    return {"url": response}


@router.get("/images/gallery/{product_name}")
async def get_image_gallery(product_name: str):
    """
    Get all image keys for a product from S3.
    Assumes images are named like 'product_name_1.jpg', 'product_name_2.jpg', etc.
    """
    try:
        response = s3.list_objects_v2(
            Bucket=AWS_S3_BUCKET_NAME,
            Prefix=product_name
        )

        if 'Contents' not in response:
            return []

        # Extract the filename without extension
        image_keys = [os.path.splitext(obj['Key'])[0] for obj in response['Contents']]
        return image_keys

    except Exception as e:
        logger.error(f"Error listing images for {product_name}: {e}")
        raise HTTPException(status_code=500, detail="Error listing images")


@router.get("/images/{filename}")
async def get_image(filename: str, width: int = 1200, quality: int = 90):
    """
    Get image from S3.
    If width resize is needed, image is processed; otherwise served directly via presigned URL.
    """
    filename = filename + ".jpg"
    try:
        # Check the image metadata first (HEAD request) to get size without downloading
        head = s3.head_object(Bucket=AWS_S3_BUCKET_NAME, Key=filename)

        # If no resize is needed, redirect to a presigned GET URL to serve original bytes
        presigned_url = s3.generate_presigned_url(
            ClientMethod="get_object",
            ExpiresIn=3600,
            Params={"Bucket": AWS_S3_BUCKET_NAME, "Key": filename}
        )
        return RedirectResponse(url=presigned_url)

    except Exception as e:
        if hasattr(e, 'response') and e.response.get('Error', {}).get('Code') in ('NoSuchKey', '404'):
            raise HTTPException(status_code=404, detail="Image not found in S3")
        logger.error(f"Error fetching image {filename}: {e}")
        raise HTTPException(status_code=404, detail="Image not found")
