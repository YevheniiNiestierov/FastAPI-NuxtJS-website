"""
One-time S3 image optimisation (safe to re-run).

For every product image "<title>_<n>.<ext>" in the bucket:
  1. re-encodes the original as WebP, max 1200px on the long side (only when that is smaller),
  2. creates the resized variants "<title>_<n>-w<width>.webp" (200 / 480 / 800 px wide) that the
     Cloudflare Worker serves for "?w=<width>".

Run: python one_time_images_optimization_script.py          (uses the root .env credentials)
     python one_time_images_optimization_script.py --dry-run
Keep VARIANT_WIDTHS in sync with app/images/router.py and cloudflare-worker/worker.js.
"""
import io
import os
import re
import sys

import boto3
import dotenv
from PIL import Image, ImageOps

dotenv.load_dotenv()

S3_BUCKET = os.environ.get("AWS_S3_BUCKET_NAME", "natur-savon-images")
MAX_DIMENSION = 1200
WEBP_QUALITY = 80
VARIANT_QUALITY = 78
VARIANT_WIDTHS = (200, 480, 800)
CACHE_CONTROL = "public, max-age=31536000, immutable"
DRY_RUN = "--dry-run" in sys.argv

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.environ["AWS_S3_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_S3_SECRET_ACCESS_KEY"],
    region_name=os.environ.get("AWS_S3_REGION_NAME", "eu-north-1"),
)

IMAGE_EXTENSIONS = (".webp", ".jpg", ".jpeg", ".png")
VARIANT_RE = re.compile(r"-w\d+$")


def encode_webp(img: Image.Image, quality: int) -> bytes:
    buffer = io.BytesIO()
    img.save(buffer, format="WEBP", quality=quality, method=6)
    return buffer.getvalue()


def put_webp(key: str, body: bytes) -> None:
    if DRY_RUN:
        return
    s3.put_object(
        Bucket=S3_BUCKET, Key=key, Body=body,
        ContentType="image/webp", CacheControl=CACHE_CONTROL,
    )


def existing_keys() -> set[str]:
    keys = set()
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=S3_BUCKET):
        keys.update(obj["Key"] for obj in page.get("Contents", []))
    return keys


def optimize_bucket():
    keys = existing_keys()
    for key in sorted(keys):
        base, ext = os.path.splitext(key)
        if ext.lower() not in IMAGE_EXTENSIONS or VARIANT_RE.search(base) or base.startswith("__tmp__"):
            continue

        print(f"Processing: {key}")
        raw = s3.get_object(Bucket=S3_BUCKET, Key=key)["Body"].read()
        with Image.open(io.BytesIO(raw)) as src:
            img = ImageOps.exif_transpose(src)
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")

            # 1. original: downscale to MAX_DIMENSION, replace only if it gets smaller
            main = img.copy()
            main.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)
            main_bytes = encode_webp(main, WEBP_QUALITY)
            if ext.lower() != ".webp":
                print(f"  note: {key} is not .webp; original left untouched")
            elif len(main_bytes) < len(raw):
                put_webp(key, main_bytes)
                print(f"  original: {len(raw) / 1024:.0f} KB -> {len(main_bytes) / 1024:.0f} KB")

            # 2. resized variants (never upscaled)
            for width in VARIANT_WIDTHS:
                variant_key = f"{base}-w{width}.webp"
                if variant_key in keys:
                    continue
                scale = min(1.0, width / img.width)
                size = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
                variant = img.resize(size, Image.Resampling.LANCZOS)
                data = encode_webp(variant, VARIANT_QUALITY)
                put_webp(variant_key, data)
                print(f"  variant w{width}: {len(data) / 1024:.0f} KB")


if __name__ == "__main__":
    optimize_bucket()