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
- **Images**: Served from AWS S3 with gallery support (multiple images per product, hover effect on product listing).

## Infrastructure & Deployment

- **Containerized** with Docker Compose: `db` (PostgreSQL), `backend` (FastAPI on port 8000), `frontend` (Nuxt on port 3000).
- **Reverse proxy**: Cloudflare sits in front, handling HTTPS and domain routing.
- **API domain**: `https://api.natur-savon.com.ua` → proxied to backend container.
- **Frontend domain**: `https://natur-savon.com.ua` → proxied to frontend container.

## SEO Setup (added April 2026)

- **Google Search Console** verification meta tag added globally via `nuxt.config.ts`.
- **Dynamic sitemap** at `/sitemap.xml` — Nuxt server route that fetches all products from FastAPI and generates valid XML automatically.
- **`robots.txt`** — blocks `/login`, `/order`, `/manager` from crawlers; points to sitemap.
- **Canonical URL** `<link rel="canonical">` set to `https://natur-savon.com.ua` to prevent www/non-www duplicate content.
- **Cloudflare Redirect Rule** — 301 permanent redirect from `www.natur-savon.com.ua/*` → `https://natur-savon.com.ua/${1}`.

## Future Enhancements

- **Extended Authentication**: Enhancements to the authentication system to cover more use cases and integration.
- **Order notifications**: Telegram bot integration for new order alerts (partially implemented in `bot.py`).