from fastapi import APIRouter, Response, HTTPException
from app.s3.s3_config import s3, S3_BUCKET_NAME

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
            "Bucket" : S3_BUCKET_NAME,
            "Key" : filename,
            "ContentType" : "image/jpeg"
        },
    )
    return {"url": response}


@router.get("/images/{filename}")
async def get_image(filename: str):
    try:
        filename = filename + ".jpg"
        # get object from s3
        response = s3.get_object(
            Bucket=S3_BUCKET_NAME,
            Key=filename
        )
        image_content = response['Body'].read()
        # Determine the content type based on the file extension
        content_type = response['ContentType']

        # Create a FastAPI response with the image content and appropriate content type
        return Response(content=image_content, media_type=content_type)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Image not found")


