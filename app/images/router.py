from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from app.s3.s3_config import s3, AWS_S3_BUCKET_NAME
from app.auth.jwt import get_current_admin
import logging
import os
import re
import uuid
from urllib.parse import quote

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Image"],
    prefix="/image"
)

EXTENSIONS = (".webp", ".jpg", ".jpeg", ".png")

# Images are served by the Cloudflare Worker (CDN_BASE); fall back to the public S3 URL.
CDN_OR_S3_BASE = (
    os.environ.get("CDN_BASE", "").rstrip("/")
    or f"https://{AWS_S3_BUCKET_NAME}.s3.amazonaws.com"
)


class ReorderRequest(BaseModel):
    keys: List[str]


def _resolve_s3_key(base: str):
    """Return the full S3 object key for a base name (tries each known extension)."""
    for ext in EXTENSIONS:
        try:
            s3.head_object(Bucket=AWS_S3_BUCKET_NAME, Key=base + ext)
            return base + ext
        except Exception:
            continue
    return None


def _build_cdn_url(full_key: str, last_modified) -> str:
    version = int(last_modified.timestamp())
    return f"{CDN_OR_S3_BASE}/{quote(full_key, safe='')}?v={version}"


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
def get_image_gallery(product_name: str):
    """
    Images for a product in display order:
    [{"key": "<base name>", "cdn_url": "<base>/<encoded key>?v=<last-modified>"}].
    Images are named 'product_name_1.webp', 'product_name_2.webp', ...
    (a legacy single 'product_name.jpg' is also returned).
    """
    try:
        pattern = re.compile(rf"^{re.escape(product_name)}(?:_(\d+))?$")
        found = {}
        for page in s3.get_paginator("list_objects_v2").paginate(
            Bucket=AWS_S3_BUCKET_NAME, Prefix=product_name
        ):
            for obj in page.get("Contents", []):
                base = os.path.splitext(obj["Key"])[0]
                match = pattern.match(base)
                if match:
                    order = int(match.group(1)) if match.group(1) else 0
                    found[base] = (order, obj["Key"], obj["LastModified"])
        return [
            {"key": base, "cdn_url": _build_cdn_url(full_key, modified)}
            for base, (_, full_key, modified) in sorted(found.items(), key=lambda kv: kv[1][0])
        ]

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
        key = _resolve_s3_key(filename)
        if not key:
            raise HTTPException(status_code=404, detail="Image not found")
        s3.delete_object(Bucket=AWS_S3_BUCKET_NAME, Key=key)
        return {"message": "Image deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting image {filename}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting image")


