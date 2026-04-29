This project is a web application developed using the **FastAPI** framework for the backend and **NuxtJS** for the frontend. The application leverages **PostgreSQL** for relational storage and **AWS S3** for image storage, delivered globally via **Cloudflare CDN**.

## Features

- **Backend**: Built with FastAPI (fully async — `asyncpg` + SQLAlchemy 2.0 async engine).
- **Frontend**: Developed using NuxtJS.
- **Storage**: PostgreSQL (via async SQLAlchemy 2.0) + AWS S3 for images.
- **CDN**: Cloudflare proxies `assets.natur-savon.com.ua` → S3, serving images with edge caching — FastAPI is never involved in image delivery.
- **Cart and Order Logic**: Session-based cart for anonymous users using browser `localStorage` UUIDs as session IDs.
- **User Management and Authentication**: JWT-based authentication with admin role support.

## Current State Details

- **Authentication**: JWT tokens with role-based access (`is_admin` flag). Admin panel available at `/manager`.
- **Cart**: Anonymous session cart stored in PostgreSQL, keyed by session UUID from `localStorage`.
- **Images**: Stored in AWS S3 (`natur-savon-images`, region `eu-north-1`). Delivered directly via Cloudflare CDN at `https://assets.natur-savon.com.ua/{s3_key}` — no FastAPI redirect involved. Gallery support with multiple images per product and hover effect on product listing. New uploads are automatically converted to **WebP** in-browser for better performance.

## Infrastructure & Deployment

- **Containerized** with Docker Compose: `db` (PostgreSQL), `backend` (FastAPI on port 8000), `frontend` (Nuxt on port 3000).
- **Reverse proxy**: Cloudflare sits in front, handling HTTPS, domain routing, and image CDN caching.
- **API domain**: `https://api.natur-savon.com.ua` → proxied to backend container.
- **Frontend domain**: `https://natur-savon.com.ua` → proxied to frontend container.
- **Assets CDN**: `https://assets.natur-savon.com.ua` → Cloudflare Worker (`s3-image-proxy`) → S3 bucket `natur-savon-images`. Worker adds `Cache-Control: public, max-age=31536000, immutable` + Cloudflare edge cache TTL 1 year.

## Async Architecture (refactored April 2026)

### Backend — fully async SQLAlchemy 2.0

All six routers (products, cart, order, users, auth, images) are now fully async. The sync `get_db()` dependency is no longer called by any route.

| Layer | Before | After |
|---|---|---|
| DB driver | `psycopg2` (sync) | `asyncpg` (async) |
| Engine | `create_engine` | `create_async_engine` |
| Session | `Session` / `sessionmaker` | `AsyncSession` / `async_sessionmaker` |
| Dependency | `get_db()` sync generator | `get_async_db()` async generator |
| Query style | `db.query(Model).filter(...)` | `await db.execute(select(Model).where(...))` |
| Route handlers | `def` | `async def` |
| Startup hook | `@router.on_event("startup")` *(deprecated)* | `lifespan` context manager on `FastAPI` |
| `get_current_admin` | sync, used sync `get_db` | async, uses `get_async_db` |
| Telegram notify | `send_message(...)` blocking call | `await asyncio.to_thread(send_message, ...)` |

#### Startup / shutdown (`main.py` lifespan)
```python
@asynccontextmanager
async def lifespan(app):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # DDL via async engine
    seed_types_and_flavours(SessionLocal())             # one-shot seed (sync)
    yield
    await async_engine.dispose()                       # graceful shutdown
```

### N+1 problems — eliminated at two layers

**Layer 1 — Frontend → Backend (products page load):**

**Before:** The frontend called `GET /product/products` (1 request) then fired `GET /image/images/gallery/{title}` for **every single product** (N requests). Under 20 products that was 21 HTTP round-trips on every page load.

**After:** `GET /product/products` returns products **with their gallery images embedded**. The backend performs one paginated S3 `list_objects_v2` call for the entire bucket and one async DB query — both run **concurrently** via `asyncio.gather`:

```python
products, gallery = await asyncio.gather(
    crud.get_products(db),      # 1 DB round-trip
    crud.fetch_all_gallery(),   # 1 S3 listing (paginated, asyncio.to_thread)
)
```

Images are then distributed to each product in Python. The response shape is:
```jsonc
[
  {
    "id": "...",
    "title": "Мило",
    // ...other product fields...
    "images": [                          // ← NEW: embedded gallery
      { "key": "Мило_1", "cdn_url": "https://assets.natur-savon.com.ua/..." },
      { "key": "Мило_2", "cdn_url": "https://assets.natur-savon.com.ua/..." }
    ]
  }
]
```

> `boto3` is synchronous. All S3 calls in async routes are wrapped with `asyncio.to_thread()` so they execute in a thread-pool worker without blocking the event loop.

### Pydantic schemas
Two new models added to `products/schemas.py`:
```python
class ImageItem(BaseModel):
    key: str       # S3 base key without extension
    cdn_url: str   # ready-to-use Cloudflare CDN URL

class ProductWithImages(Product):
    images: List[ImageItem] = []
```
All `product.dict()` calls updated to `product.model_dump()` (Pydantic v2).

### Frontend (`pages/products/index.vue`)
`fetchProductGallery()` and its `Promise.all(products.map(...))` loop are completely removed. `fetchProducts()` now maps the embedded `images` array directly:
```js
const images = product.images ?? [];
imageUrl:      images[0]?.cdn_url ?? '',
hoverImageUrl: images[1]?.cdn_url ?? null,
imageKeys:     images.map(img => img.key),
```
Page load goes from **1 + N** HTTP requests to **1**.

**Layer 2 — Backend cart queries:**

**Before:** `get_products_and_total_sum` and `update_cart_total` issued a separate `SELECT` for each cart item's product — N+1 inside the backend.

**After:** Both functions use `selectinload(CartItemModel.product)` to load all associated products in a single second query (two total), then compute the total price in Python.

## Environment Variables

### Backend (`app/.env`)

| Variable | Description |
|---|---|
| `AWS_S3_ACCESS_KEY_ID` | S3 IAM key |
| `AWS_S3_SECRET_ACCESS_KEY` | S3 IAM secret |
| `AWS_S3_REGION_NAME` | S3 region (e.g. `eu-north-1`) |
| `ASSETS_CDN_BASE_URL` | Cloudflare CDN base URL (e.g. `https://assets.natur-savon.com.ua`) |
| `JWT_SECRET_KEY` | JWT signing secret |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` / `ADMIN_EMAIL` | Seed admin credentials |

### Frontend

| Variable | Description |
|---|---|
| `NUXT_PUBLIC_API_BASE` | FastAPI base URL (e.g. `https://api.natur-savon.com.ua`) |
| `NUXT_PUBLIC_CDN_BASE` | Cloudflare CDN base URL (e.g. `https://assets.natur-savon.com.ua`) |

## Image Delivery Architecture (added April 2026)

### Request flow
```
Browser → https://assets.natur-savon.com.ua/Soap_1.webp
        → Cloudflare Edge (route: assets.natur-savon.com.ua/*)
            CACHE HIT  → served from edge cache (<15 ms), S3 & FastAPI never contacted
            CACHE MISS → Worker fetches from S3, caches at edge, serves (~100–200 ms, once per PoP)
        → Worker: s3-image-proxy  (cloudflare-worker/worker.js)
        → S3: https://natur-savon-images.s3.eu-north-1.amazonaws.com/Soap_1.webp
```

### Image API endpoints (`/image`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/images/upload` | Admin | Returns a presigned PUT URL so the browser uploads directly to S3 |
| `GET` | `/images/gallery/{product_name}` | Public | Lists all images for a product: `[{ key, cdn_url }]` |
| `DELETE` | `/images/{filename}` | Admin | Deletes an image from S3 (auto-detects extension) |
| `POST` | `/images/reorder` | Admin | Renames S3 objects to apply a new display order |

> The old `GET /images/{filename}` and `GET /images/first/{product_name}` presigned-redirect endpoints have been **removed**. The frontend constructs CDN URLs directly from the gallery response's `cdn_url` field.

### Cloudflare DNS & Worker setup
1. **CNAME record** — `assets` → `natur-savon-images.s3.eu-north-1.amazonaws.com` (Proxied / orange cloud).
2. **Cloudflare Worker** — `s3-image-proxy` intercepts all `assets.natur-savon.com.ua/*` requests, fetches the object from S3, and re-serves it with `Cache-Control: public, max-age=31536000, immutable` and `cf: { cacheTtl: 31536000 }` for edge caching. Worker source: `cloudflare-worker/worker.js`. Deploy with:
   ```powershell
   cd cloudflare-worker
   npx wrangler deploy
   ```
3. **S3 Bucket Policy** — `s3:GetObject` public read (no `ListBucket`). The Worker adds the access-control layer; direct S3 traffic bypasses the CDN cache but the bucket can still serve it as a fallback.

## Manager Panel (`/manager`)

- **Create products**: title, description, instructions, price, weight, flavour, type + image upload.
- **Edit products**: all fields editable via modal, including full image management.
- **Image management** (added April 2026):
  - View existing product images with numbered order badges (thumbnails loaded from Cloudflare CDN).
  - **Reorder** existing images using ▲▼ buttons — changes are applied to S3 on save.
  - **Delete** individual existing images directly from S3.
  - **Add new images** to an existing product with preview and reorder support before upload.
  - All uploads are **converted to WebP** client-side (Canvas API) before being sent to S3 for optimal performance.
  - Backend auto-detects image extension (`.webp`, `.jpg`, `.jpeg`, `.png`) for deleting and reordering — fully backward-compatible with existing `.jpg` images.
- **Delete products**: confirmation modal before deletion; also clears related cart items.
- **Manage flavours & types**: add new options inline without leaving the page.

## SEO Setup (added April 2026)

- **Google Search Console** verification meta tag added globally via `nuxt.config.ts`.
- **Dynamic sitemap** at `/sitemap.xml` — Nuxt server route that fetches all products from FastAPI and generates valid XML automatically.
- **`robots.txt`** — blocks `/login`, `/order`, `/manager` from crawlers; points to sitemap.
- **Canonical URL** `<link rel="canonical">` set to `https://natur-savon.com.ua` to prevent www/non-www duplicate content.
- **Cloudflare Redirect Rule** — 301 permanent redirect from `www.natur-savon.com.ua/*` → `https://natur-savon.com.ua/${1}`.
- **CDN image URLs** — images served via direct `https://assets.natur-savon.com.ua/...` URLs (no 302 redirects), which Googlebot indexes without ambiguity.

## Future Enhancements

- **Extended Authentication**: Enhancements to the authentication system to cover more use cases and integration.
- **Order notifications**: Telegram bot integration for new order alerts (partially implemented in `bot.py`).
- **Image bulk migration**: Script to convert existing `.jpg` S3 images to WebP and update S3 object metadata.
