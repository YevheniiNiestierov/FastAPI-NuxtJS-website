from fastapi import APIRouter, HTTPException, Depends
from app.s3.s3_config import s3, AWS_S3_BUCKET_NAME, CDN_OR_S3_BASE
from app.auth.jwt import get_current_admin
from pydantic import BaseModel
from typing import List
from urllib.parse import quote
import logging
import os
import re

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Image"],
    prefix="/image"
)

_IMAGE_EXTENSIONS = ['.webp', '.jpg', '.jpeg', '.png']


def _resolve_s3_key(base_key: str) -> str:
    """Find the actual S3 key for a base filename (no extension) by trying common image extensions."""
    for ext in _IMAGE_EXTENSIONS:
        key = base_key + ext
        try:
            s3.head_object(Bucket=AWS_S3_BUCKET_NAME, Key=key)
            return key
        except Exception:
            continue
    raise HTTPException(status_code=404, detail=f"Image '{base_key}' not found in S3")


# ---------------------------------------------------------------------------
# Upload (admin – presigned PUT so the browser uploads directly to S3)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Gallery – returns image keys AND their ready-to-use Cloudflare CDN URLs.
# The frontend should use cdn_url directly for <img src>; no FastAPI hop needed.
# ---------------------------------------------------------------------------

@router.get("/images/gallery/{product_name}")
async def get_image_gallery(product_name: str):
    """
    List all images for a product from S3.
    Returns objects: { key: str (without extension), cdn_url: str (full CDN URL) }
    """
    try:
        response = s3.list_objects_v2(
            Bucket=AWS_S3_BUCKET_NAME,
            Prefix=product_name
        )

        if 'Contents' not in response:
            return []

        result = []
        for obj in response['Contents']:
            full_key = obj['Key']                            # e.g. "Мило_1.webp"
            base_key = os.path.splitext(full_key)[0]        # e.g. "Мило_1"
            encoded_key = quote(full_key, safe='')           # e.g. "%D0%9C%D0%B8%D0%BB%D0%BE_1.webp"
            cdn_url = f"{CDN_OR_S3_BASE}/{encoded_key}"     # always a valid absolute URL
            result.append({"key": base_key, "cdn_url": cdn_url})

        return result

    except Exception as e:
        logger.error(f"Error listing images for {product_name}: {e}")
        raise HTTPException(status_code=500, detail="Error listing images")


# ---------------------------------------------------------------------------
# Delete & Reorder (admin only – still go through FastAPI + S3 SDK)
# ---------------------------------------------------------------------------

@router.delete("/images/{filename}")
def delete_image(filename: str, current_user=Depends(get_current_admin)):
    """Delete an image from S3 by base key (without extension). Auto-detects the actual extension."""
    try:
        actual_key = _resolve_s3_key(filename)
        s3.delete_object(Bucket=AWS_S3_BUCKET_NAME, Key=actual_key)
        return {"message": f"Deleted {actual_key}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting image '{filename}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ReorderRequest(BaseModel):
    keys: List[str]  # keys without extension, in new desired order


@router.post("/images/reorder")
def reorder_images(body: ReorderRequest, current_user=Depends(get_current_admin)):
    """
    Reorder images in S3 by renaming them to match their new position.
    Accepts a list of base keys (without extension) in the desired final order.
    Auto-detects each image's actual extension. Returns the new ordered base keys.
    """
    keys = body.keys
    if not keys:
        return {"keys": []}

    # Derive base product name by stripping trailing _N suffix from first key
    base = re.sub(r'_\d+$', '', keys[0])

    try:
        # Resolve the actual S3 key (with extension) for each base key
        actual_keys = [_resolve_s3_key(k) for k in keys]

        # Step 1: copy each to a uniquely named temp key (preserving extension)
        temp_entries = []  # [(temp_key, ext)]
        for i, actual_key in enumerate(actual_keys):
            ext = os.path.splitext(actual_key)[1]   # e.g. '.webp' or '.jpg'
            temp_key = f"__reorder_temp_{i}{ext}"
            s3.copy_object(
                Bucket=AWS_S3_BUCKET_NAME,
                CopySource={"Bucket": AWS_S3_BUCKET_NAME, "Key": actual_key},
                Key=temp_key
            )
            temp_entries.append((temp_key, ext))

        # Step 2: delete originals
        for actual_key in actual_keys:
            s3.delete_object(Bucket=AWS_S3_BUCKET_NAME, Key=actual_key)

        # Step 3: copy from temp to final numbered names (preserve each file's extension)
        new_keys = []
        for i, (temp_key, ext) in enumerate(temp_entries):
            new_key_full = f"{base}_{i + 1}{ext}"
            s3.copy_object(
                Bucket=AWS_S3_BUCKET_NAME,
                CopySource={"Bucket": AWS_S3_BUCKET_NAME, "Key": temp_key},
                Key=new_key_full
            )
            new_keys.append(f"{base}_{i + 1}")  # return base key without extension

        # Step 4: delete temp keys
        for temp_key, _ in temp_entries:
            s3.delete_object(Bucket=AWS_S3_BUCKET_NAME, Key=temp_key)

        return {"keys": new_keys}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reordering images: {e}")
        raise HTTPException(status_code=500, detail=str(e))
