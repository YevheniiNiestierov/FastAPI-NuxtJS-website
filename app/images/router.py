from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from app.s3.s3_config import s3, AWS_S3_BUCKET_NAME
from app.auth.jwt import get_current_admin
import logging
import os
import re
import uuid
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Image"],
    prefix="/image"
)

EXTENSIONS = (".webp", ".jpg")


class ReorderRequest(BaseModel):
    keys: List[str]


def _find_key(base: str):
    """Return the S3 object key for a base name (tries .webp, then legacy .jpg)."""
    for ext in EXTENSIONS:
        try:
            s3.head_object(Bucket=AWS_S3_BUCKET_NAME, Key=base + ext)
            return base + ext
        except Exception:
            continue
    return None


@router.get("/images/upload")
def get_upload_url(filename: str, content_type: str = "image/jpeg", expires=9999):
    allowed_types = ["image/jpeg", "image/png", "image/heic", "image/webp"]
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
    Get all image keys (without extension) for a product from S3, in display order.
    Images are named 'product_name_1.webp', 'product_name_2.webp', ...
    (a legacy single 'product_name.jpg' is also returned).
    """
    try:
        response = s3.list_objects_v2(
            Bucket=AWS_S3_BUCKET_NAME,
            Prefix=product_name
        )
        pattern = re.compile(rf"^{re.escape(product_name)}(?:_(\d+))?$")
        found = {}
        for obj in response.get('Contents', []):
            base = os.path.splitext(obj['Key'])[0]
            match = pattern.match(base)
            if match:
                found[base] = int(match.group(1)) if match.group(1) else 0
        return [key for key, _ in sorted(found.items(), key=lambda kv: kv[1])]

    except Exception as e:
        logger.error(f"Error listing images for {product_name}: {e}")
        raise HTTPException(status_code=500, detail="Error listing images")


@router.post("/images/reorder")
def reorder_images(data: ReorderRequest, current_user=Depends(get_current_admin)):
    """Rename a product's images to <prefix>_1, <prefix>_2, ... following the given order."""
    keys = data.keys
    if not keys:
        return {"keys": []}

    prefixes = set()
    for key in keys:
        match = re.match(r"^(.+)_(\d+)$", key)
        if not match:
            raise HTTPException(status_code=400, detail=f"Invalid image key: {key}")
        prefixes.add(match.group(1))
    if len(prefixes) != 1:
        raise HTTPException(status_code=400, detail="All keys must belong to one product")
    prefix = prefixes.pop()

    try:
        # Phase 1: copy to temporary keys so renames can't overwrite each other
        temp_keys = []
        for key in keys:
            src = _resolve_s3_key(key)
            if not src:
                raise HTTPException(status_code=404, detail=f"Image not found: {key}")
            tmp = f"__tmp__{uuid.uuid4().hex}.webp"
            s3.copy_object(
                Bucket=AWS_S3_BUCKET_NAME,
                CopySource={"Bucket": AWS_S3_BUCKET_NAME, "Key": src},
                Key=tmp,
            )
            temp_keys.append((src, tmp))
        for src, _ in temp_keys:
            s3.delete_object(Bucket=AWS_S3_BUCKET_NAME, Key=src)

        # Phase 2: copy temporary keys to their final names
        new_keys = []
        for index, (_, tmp) in enumerate(temp_keys, start=1):
            base = f"{prefix}_{index}"
            s3.copy_object(
                Bucket=AWS_S3_BUCKET_NAME,
                CopySource={"Bucket": AWS_S3_BUCKET_NAME, "Key": tmp},
                Key=base + ".webp",
            )
            s3.delete_object(Bucket=AWS_S3_BUCKET_NAME, Key=tmp)
            new_keys.append(base)
        return {"keys": new_keys}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reordering images: {e}")
        raise HTTPException(status_code=500, detail="Error reordering images")


@router.delete("/images/{filename}")
def delete_image(filename: str, current_user=Depends(get_current_admin)):
    try:
        for ext in EXTENSIONS:
            s3.delete_object(Bucket=AWS_S3_BUCKET_NAME, Key=filename + ext)
        return {"message": "Image deleted"}
    except Exception as e:
        logger.error(f"Error deleting image {filename}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting image")


@router.get("/images/{filename}")
async def get_image(filename: str, width: int = 1200, quality: int = 90):
    """
    Get optimized image from S3
    - width: max width in pixels (default 1200)
    - quality: JPEG quality 1-100 (default 90)
    A name without a numeric suffix (e.g. a product title) falls back to its first image.
    """
    key = _find_key(filename) or _find_key(f"{filename}_1")
    if not key:
        raise HTTPException(status_code=404, detail="Image not found")
    try:
        response = s3.get_object(
            Bucket=AWS_S3_BUCKET_NAME,
            Key=key
        )
        image_content = response['Body'].read()

        # Open and optimize image
        img = Image.open(BytesIO(image_content))

        # Convert HEIC/PNG/WebP with alpha to RGB if needed
        if img.mode in ('RGBA', 'P', 'LA'):
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
        logger.error(f"Error fetching image {key}: {e}")
        raise HTTPException(status_code=404, detail="Image not found")
