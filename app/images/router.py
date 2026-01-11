from fastapi import APIRouter, Response, HTTPException
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


@router.get("/images/{filename}")
async def get_image(filename: str, width: int = 1200, quality: int = 90):
    """
    Get optimized image from S3
    - width: max width in pixels (default 1200)
    - quality: JPEG quality 1-100 (default 90)
    """
    filename = filename + ".jpg"
    try:
        response = s3.get_object(
            Bucket=AWS_S3_BUCKET_NAME,
            Key=filename
        )
        image_content = response['Body'].read()

        # Open and optimize image
        img = Image.open(BytesIO(image_content))

        # Convert HEIC/PNG to RGB if needed
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # Resize if larger than target width
        if img.width > width:
            ratio = width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((width, new_height), Image.Resampling.LANCZOS)

        # Save optimized image to buffer
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        buffer.seek(0)

        return Response(content=buffer.getvalue(), media_type="image/jpeg")

    except Exception as e:
        if hasattr(e, 'response') and e.response.get('Error', {}).get('Code') == 'NoSuchKey':
            raise HTTPException(status_code=404, detail="Image not found in S3")
        logger.error(f"Error fetching image {filename}: {e}")
        raise HTTPException(status_code=404, detail="Image not found")
