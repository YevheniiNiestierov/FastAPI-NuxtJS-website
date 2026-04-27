This project is a web application developed using the **FastAPI** framework for the backend and **NuxtJS** for the frontend. The application leverages **PostgreSQL** for relational storage and **AWS S3** for image storage, delivered globally via **Cloudflare CDN**.

## Features

- **Backend**: Built with FastAPI.
- **Frontend**: Developed using NuxtJS.
- **Storage**: PostgreSQL (via SQLAlchemy) + AWS S3 for images.
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
- **Assets CDN**: `https://assets.natur-savon.com.ua` → Cloudflare CNAME → `natur-savon-images.s3.eu-north-1.amazonaws.com`. Edge cache TTL: 1 year. Browser TTL: 7 days.

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
        → Cloudflare Edge
            CACHE HIT  → served from edge RAM (<15 ms), S3 & FastAPI never contacted
            CACHE MISS → Cloudflare fetches from S3, caches, serves (~100–200 ms, once per PoP)
```

### Image API endpoints (`/image`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/images/upload` | Admin | Returns a presigned PUT URL so the browser uploads directly to S3 |
| `GET` | `/images/gallery/{product_name}` | Public | Lists all images for a product: `[{ key, cdn_url }]` |
| `DELETE` | `/images/{filename}` | Admin | Deletes an image from S3 (auto-detects extension) |
| `POST` | `/images/reorder` | Admin | Renames S3 objects to apply a new display order |

> The old `GET /images/{filename}` and `GET /images/first/{product_name}` presigned-redirect endpoints have been **removed**. The frontend constructs CDN URLs directly from the gallery response's `cdn_url` field.

### Cloudflare DNS & Cache setup
1. **CNAME record** — `assets` → `natur-savon-images.s3.eu-north-1.amazonaws.com` (Proxied / orange cloud).
2. **Cache Rule** — expression `(http.host eq "assets.natur-savon.com.ua")`, Edge TTL override 1 year, Browser TTL override 7 days.
3. **S3 Bucket Policy** — `s3:GetObject` only (no `ListBucket`). Optionally restricted to Cloudflare IP ranges for direct-S3 bypass prevention.

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
- **Cloudflare IP whitelist**: Restrict S3 bucket policy to Cloudflare IP ranges only, preventing direct-to-S3 traffic that bypasses CDN caching.
