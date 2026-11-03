# Natur Savon — web shop

Online shop for handmade soap: a **FastAPI** backend, a **Nuxt 3** frontend, **PostgreSQL** for data and **AWS S3** (behind a **Cloudflare Worker** CDN) for product images.

## Architecture

| Part | Tech | Notes |
| --- | --- | --- |
| Backend (`app/`) | FastAPI, SQLAlchemy 2 (sync), psycopg2 | REST API on port 8000 |
| Frontend (`frontend/`) | Nuxt 3 (Vue 3) | Store, checkout and manager panel, port 3000 |
| Database | PostgreSQL 16 | Products, types/flavours, carts, orders, users |
| Images | S3 bucket `natur-savon-images` | Uploaded straight from the browser with presigned URLs |
| CDN | Cloudflare Worker `s3-image-proxy` (`cloudflare-worker/`) | `assets.natur-savon.com.ua` → S3, edge cached |
| Notifications | Telegram bot (`app/bot.py`) | Message on every new order |

Carts are stored in PostgreSQL and identified by an anonymous session ID (`Session-ID` header, a UUID kept in the browser's `localStorage`). Admin authentication uses JWT (`/login`, token carries `is_admin`).

### Backend layout

```
app/
  main.py          FastAPI app, CORS, routers
  create_admin.py  Runs on container start: creates tables, adds missing columns,
                   seeds product types/flavours, (re)creates the admin user
  postgres/        database.py — engine, SessionLocal, Base, get_db()
  auth/            JWT + /login
  users/ products/ cart/ order/ images/   routers, crud, models, schemas
  s3/              boto3 client
```

### Frontend pages

`/products` (store, `/` redirects here), `/products/[id]`, `/order` (checkout), `/login`, `/manager` (admin: products, types/flavours, images), `/about`, `/contract`.

## Run locally

```bash
cp .env.example .env        # fill in JWT_SECRET_KEY, AWS_*, BOT_*; see "Environment"
docker compose up -d --build
```

- Site: http://localhost:3000 — API: http://localhost:8000 (docs at `/docs`)
- PostgreSQL is published on `127.0.0.1:5433`.
- `docker-compose.yml` hard-codes `NUXT_PUBLIC_API_BASE=http://localhost:8000` and an empty CDN, so images are served through the API and production URLs in `.env` are ignored.
- The admin user is recreated on every backend start from `ADMIN_EMAIL` / `ADMIN_PASSWORD` (defaults: `admin@example.com` and a built-in password — set your own).
- Reset the local database: `docker compose down -v`.

## Deploy (VPS)

```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
# optional: echo "COMPOSE_FILE=docker-compose.prod.yml" >> .env   # then plain `docker compose ...`
```

`docker-compose.prod.yml` publishes the site and API only on `127.0.0.1:3000` / `127.0.0.1:8000` and does not publish PostgreSQL. Put a reverse proxy or tunnel (nginx, Caddy, cloudflared) in front:

- `natur-savon.com.ua` → `127.0.0.1:3000`
- `api.natur-savon.com.ua` → `127.0.0.1:8000`

CORS origins are listed in `app/main.py` — add any new domain there.

## Environment

One `.env` in the project root is used by Docker Compose and by the backend (`env_file`). See `.env.example`. Never commit it.

| Variable | Purpose |
| --- | --- |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Database credentials (read only when the volume is first created) |
| `JWT_SECRET_KEY` | Signs admin tokens |
| `ADMIN_EMAIL`, `ADMIN_USERNAME`, `ADMIN_PASSWORD` | Admin account created on start |
| `BOT_API_TOKEN`, `CHAT_ID` | Telegram order notifications |
| `AWS_S3_ACCESS_KEY_ID`, `AWS_S3_SECRET_ACCESS_KEY`, `AWS_S3_REGION_NAME` | S3 access |
| `NUXT_PUBLIC_API_BASE` | Public API URL used by the browser (production) |
| `CDN_BASE`, `NUXT_PUBLIC_CDN_BASE` | Cloudflare Worker URL; empty = serve images via the API |

## Images and CDN

- Images are named `<product title>_<n>.webp` (`n` = display order). The manager page converts uploads to WebP and uploads to S3 with a presigned URL from `GET /image/images/upload`.
- With `CDN_BASE` set, `GET /product/products` returns `images[].cdn_url` = `https://assets…/<key>.webp?v=<last-modified>`. The version changes when an image is replaced or reordered, which is what allows the Worker to cache it for a year (`immutable`). Unversioned URLs are cached for 1 hour; errors are never cached.
- Deploy the Worker: `cd cloudflare-worker && npx wrangler deploy` (route `assets.natur-savon.com.ua/*`, the `assets` DNS record must be proxied).
- The S3 bucket needs public read and a CORS rule allowing `PUT` from the site origins (for browser uploads).

## Notes

- Tables are created with `Base.metadata.create_all`; it does not alter existing tables. Add new columns with an idempotent `ALTER TABLE … ADD COLUMN IF NOT EXISTS` in `app/create_admin.py` (no Alembic yet).
- Use `$fetch` (not `useFetch`) for requests made in click handlers or `onMounted` in the Nuxt app.

