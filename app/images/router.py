from fastapi import APIRouter, Response, HTTPException
from app.s3.s3_config import s3, AWS_S3_BUCKET_NAME

router = APIRouter(
    tags=["Image"],
    prefix="/image"
)


@router.get("/images/upload")
def get_upload_url(filename: str, expires=9999):
    response =s3.generate_presigned_url(
        ClientMethod = "put_object",
        ExpiresIn = expires,
        Params = {
            "Bucket" : AWS_S3_BUCKET_NAME,
            "Key" : filename,
            "ContentType" : "image/jpeg"
        },
    )
    return {"url": response}


import logging

logger = logging.getLogger(__name__)

@router.get("/images/{filename}")
async def get_image(filename: str):
    try:
        response = s3.get_object(
            Bucket=AWS_S3_BUCKET_NAME,
            Key=filename
        )
        image_content = response['Body'].read()
        content_type = response['ContentType']
        return Response(content=image_content, media_type=content_type)
    except Exception as e:
        logger.error(f"Error fetching image {filename}: {e}")
        raise HTTPException(status_code=404, detail="Image not found")




