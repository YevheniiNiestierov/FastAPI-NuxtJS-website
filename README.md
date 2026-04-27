This project is a web application developed using the **FastAPI** framework for the backend and **NuxtJS** for the frontend. The application leverages **PostgreSQL** for relational storage and **AWS S3** for image storage.

## Features

- **Backend**: Built with FastAPI.
- **Frontend**: Developed using NuxtJS.
- **Storage**: PostgreSQL (via SQLAlchemy) + AWS S3 for images.
- **Cart and Order Logic**: Session-based cart for anonymous users using browser `localStorage` UUIDs as session IDs.
- **User Management and Authentication**: JWT-based authentication with admin role support.

## Current State Details

- **Authentication**: JWT tokens with role-based access (`is_admin` flag). Admin panel available at `/manager`.
- **Cart**: Anonymous session cart stored in PostgreSQL, keyed by session UUID from `localStorage`.
- **Images**: Served from AWS S3 with gallery support (multiple images per product, hover effect on product listing). New uploads are automatically converted to **WebP** in-browser for better performance.

## Infrastructure & Deployment

- **Containerized** with Docker Compose: `db` (PostgreSQL), `backend` (FastAPI on port 8000), `frontend` (Nuxt on port 3000).
- **Reverse proxy**: Cloudflare sits in front, handling HTTPS and domain routing.
- **API domain**: `https://api.natur-savon.com.ua` → proxied to backend container.
- **Frontend domain**: `https://natur-savon.com.ua` → proxied to frontend container.

## Manager Panel (`/manager`)

- **Create products**: title, description, instructions, price, weight, flavour, type + image upload.
- **Edit products**: all fields editable via modal, including full image management.
- **Image management** (added April 2026):
  - View existing product images with numbered order badges.
  - **Reorder** existing images using ▲▼ buttons — changes are applied to S3 on save.
  - **Delete** individual existing images directly from S3.
  - **Add new images** to an existing product with preview and reorder support before upload.
  - All uploads are **converted to WebP** client-side (Canvas API) before being sent to S3 for optimal performance.
  - Backend auto-detects image extension (`.webp`, `.jpg`, `.jpeg`, `.png`) for serving, deleting, and reordering — fully backward-compatible with existing `.jpg` images.
- **Delete products**: confirmation modal before deletion; also clears related cart items.
- **Manage flavours & types**: add new options inline without leaving the page.

## SEO Setup (added April 2026)

- **Google Search Console** verification meta tag added globally via `nuxt.config.ts`.
- **Dynamic sitemap** at `/sitemap.xml` — Nuxt server route that fetches all products from FastAPI and generates valid XML automatically.
- **`robots.txt`** — blocks `/login`, `/order`, `/manager` from crawlers; points to sitemap.
- **Canonical URL** `<link rel="canonical">` set to `https://natur-savon.com.ua` to prevent www/non-www duplicate content.
- **Cloudflare Redirect Rule** — 301 permanent redirect from `www.natur-savon.com.ua/*` → `https://natur-savon.com.ua/${1}`.

## Future Enhancements

- **Extended Authentication**: Enhancements to the authentication system to cover more use cases and integration.
- **Order notifications**: Telegram bot integration for new order alerts (partially implemented in `bot.py`).
- **Image bulk migration**: Script to convert existing `.jpg` S3 images to WebP.
