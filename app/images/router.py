from fastapi import APIRouter, Response, HTTPException
from app.s3.s3_config import s3, AWS_S3_BUCKET_NAME
import logging
import os

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
async def get_image(filename: str):
    filename = filename + ".jpg"
    try:
        response = s3.get_object(
            Bucket=AWS_S3_BUCKET_NAME,
            Key=filename
        )
        image_content = response['Body'].read()

        extension_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".heic": "image/heic"
        }
        _, ext = os.path.splitext(filename.lower())
        content_type = extension_map.get(ext, "image/jpeg")

        return Response(content=image_content, media_type=content_type)
    except Exception as e:
        if hasattr(e, 'response') and e.response.get('Error', {}).get('Code') == 'NoSuchKey':
            raise HTTPException(status_code=404, detail="Image not found in S3")
        logger.error(f"Error fetching image {filename}: {e}")
        raise HTTPException(status_code=404, detail="Image not found")
