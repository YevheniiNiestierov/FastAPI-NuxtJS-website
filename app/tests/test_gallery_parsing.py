"""
Unit tests for the pure-Python S3 gallery parsing logic inside
app/products/crud.py  (fetch_all_gallery / fetch_product_gallery).

No real S3 connection is made — asyncio.to_thread is patched to return a
synthetic list of S3 objects, letting us test the parsing and grouping logic
in full isolation.
"""
import os
from unittest.mock import patch, AsyncMock

import pytest

from app.products.schemas import ImageItem

CDN_BASE = "https://test-cdn.example.com"


def _make_s3_objects(*keys: str) -> list[dict]:
    """Create a minimal S3 Contents list from a list of object keys."""
    return [{"Key": k} for k in keys]


async def _call_fetch_all_gallery(s3_keys: list[str]) -> dict:
    """Call fetch_all_gallery with a mocked S3 response."""
    from app.products.crud import fetch_all_gallery
    with patch(
        "app.products.crud.asyncio.to_thread",
        new=AsyncMock(return_value=_make_s3_objects(*s3_keys)),
    ):
        with patch("app.products.crud.CDN_OR_S3_BASE", CDN_BASE):
            return await fetch_all_gallery()


async def _call_fetch_product_gallery(product_title: str, s3_keys: list[str]) -> list[ImageItem]:
    """Call fetch_product_gallery with a mocked S3 response."""
    from app.products.crud import fetch_product_gallery
    with patch(
        "app.products.crud.asyncio.to_thread",
        new=AsyncMock(return_value=_make_s3_objects(*s3_keys)),
    ):
        with patch("app.products.crud.CDN_OR_S3_BASE", CDN_BASE):
            return await fetch_product_gallery(product_title)



# ── fetch_all_gallery ─────────────────────────────────────────────────────────

async def test_fetch_all_gallery_empty_bucket():
    result = await _call_fetch_all_gallery([])
    assert result == {}


async def test_fetch_all_gallery_groups_images_by_product():
    keys = ["Мило_1.webp", "Мило_2.webp", "Скраб_1.webp"]
    result = await _call_fetch_all_gallery(keys)

    assert set(result.keys()) == {"Мило", "Скраб"}
    assert len(result["Мило"]) == 2
    assert len(result["Скраб"]) == 1


async def test_fetch_all_gallery_sorts_images_by_numeric_suffix():
    # Delivered out of order deliberately
    keys = ["Мило_3.webp", "Мило_1.webp", "Мило_2.webp"]
    result = await _call_fetch_all_gallery(keys)

    images = result["Мило"]
    assert images[0].key == "Мило_1"
    assert images[1].key == "Мило_2"
    assert images[2].key == "Мило_3"


async def test_fetch_all_gallery_skips_keys_without_numeric_suffix():
    keys = ["logo.webp", "banner.jpg", "Мило_1.webp"]
    result = await _call_fetch_all_gallery(keys)

    assert "logo" not in result
    assert "banner" not in result
    assert "Мило" in result


async def test_fetch_all_gallery_cdn_url_contains_encoded_key():
    keys = ["Мило_1.webp"]
    result = await _call_fetch_all_gallery(keys)
    cdn_url = result["Мило"][0].cdn_url

    # URL must be absolute and contain the encoded key
    assert cdn_url.startswith(CDN_BASE)
    # Cyrillic 'М' encodes to %D0%9C etc.  Just check %D is present.
    assert "%" in cdn_url


async def test_fetch_all_gallery_returns_image_item_objects():
    keys = ["Soap_1.jpg"]
    result = await _call_fetch_all_gallery(keys)
    assert isinstance(result["Soap"][0], ImageItem)


async def test_fetch_all_gallery_handles_mixed_extensions():
    keys = ["Prod_1.webp", "Prod_2.jpg", "Prod_3.png"]
    result = await _call_fetch_all_gallery(keys)
    assert len(result["Prod"]) == 3
    # Keys should not contain the extension
    for img in result["Prod"]:
        assert "." not in img.key


# ── fetch_product_gallery ─────────────────────────────────────────────────────

async def test_fetch_product_gallery_returns_sorted_images():
    keys = ["Мило_2.webp", "Мило_1.webp"]
    result = await _call_fetch_product_gallery("Мило", keys)
    assert result[0].key == "Мило_1"
    assert result[1].key == "Мило_2"


async def test_fetch_product_gallery_empty_returns_empty_list():
    result = await _call_fetch_product_gallery("Мило", [])
    assert result == []


async def test_fetch_product_gallery_cdn_url_is_correct():
    keys = ["Soap_1.webp"]
    result = await _call_fetch_product_gallery("Soap", keys)
    assert result[0].cdn_url.startswith(CDN_BASE)
    assert "Soap_1.webp" in result[0].cdn_url or "%53" in result[0].cdn_url

