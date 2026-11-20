# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project

Natur Savon web shop: FastAPI backend (`app/`), Nuxt 3 frontend (`frontend/`), PostgreSQL, S3 images served through a Cloudflare Worker (`cloudflare-worker/`). See `README.md` for the full overview.

## Commands

```bash
docker compose up -d --build                      # local stack (site :3000, API :8000, Postgres 127.0.0.1:5433)
docker compose up -d --build backend              # rebuild one service
docker logs soap_backend --tail 50                # backend logs
docker compose -f docker-compose.prod.yml config  # validate the production file
docker compose down -v                            # wipe the local database
```

- Both services run from **built images**: after editing code you must rebuild (`--build`), a refresh is not enough. Frontend changes need `--build frontend`, backend changes `--build backend`.
- There is no test suite and no linter configured. Verify backend changes with `curl` against `localhost:8000`; verify frontend changes by rebuilding and checking the browser console.
- Log in for admin endpoints: `POST /login` (form fields `username` = email, `password`) → `access_token`; send it as `Authorization: Bearer <token>`.

## Conventions

### Backend
- Import the DB layer from `app.postgres.database` (`Base`, `engine`, `SessionLocal`, `get_db`). Do not reintroduce `app.sqlite`.
- The stack is **synchronous** SQLAlchemy 2 (`Session`, `db.query(...)`). Do not mix in `AsyncSession`.
- Layout per feature: `models.py`, `schemas.py`, `crud.py`, `router.py`. Routers get `db: Session = Depends(get_db)`; admin-only routes add `Depends(get_current_admin)`.
- Schema changes: `create_all` never alters existing tables. Add an idempotent `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` in `app/create_admin.py` (it runs on every container start, before uvicorn).
- Config comes from environment variables (`os.environ[...]`); never hard-code secrets.
- Image keys are `<product title>_<n>` without extension; objects in S3 are `.webp` (older ones may be `.jpg`). `cdn_url` carries `?v=<last-modified>` so the Worker can cache it immutably.
- Resized variants: next to each `<key>.webp` the admin upload stores `<key>-w200.webp`, `-w480.webp`, `-w800.webp`. The Worker serves them for `?w=200|480|800` and falls back to the original if a variant is missing. `VARIANT_WIDTHS` lives in 4 places and must stay in sync: `app/images/router.py`, `cloudflare-worker/worker.js`, `frontend/utils/image.ts`, `IMAGE_VARIANT_WIDTHS` in `frontend/pages/manager.vue` (plus `one_time_images_optimization_script.py`). Variants are not product images: gallery/listing code skips keys matching `_<n>-w<width>`; delete, reorder and title-rename (`rename_gallery`) move them together with the original.
- Add new CORS origins in `app/main.py`.

### Frontend
- Public content (catalog, product details, image gallery) is loaded during SSR with `await useAsyncData(key, () => $fetch(...))` so it is in the raw HTML for crawlers/LLMs. Use `$fetch` in click handlers and `onMounted` (cart, add-to-cart); avoid `useFetch` (caches by URL).
- Per-visitor state (cart, `sessionID`, admin token in `localStorage`) stays client-only: load it in `onMounted`. Browser-only APIs (`localStorage`, `crypto`, `window`) must be guarded (`import.meta.client` / `onMounted`) because pages are server-rendered.
- API URL: call `useApiBase()` (`frontend/composables/useApiBase.ts`). On the server it returns `runtimeConfig.apiBaseInternal` (`NUXT_API_BASE_INTERNAL`, `http://backend:8000` in both compose files), in the browser `public.apiBase`. Other URLs come from `useRuntimeConfig().public` (`cdnBase`, `siteUrl`); never hard-code hosts.
- SEO/GEO: every page calls `usePageSeo({ title, description, image?, noindex? })` (`frontend/composables/usePageSeo.ts`), which sets title, description, canonical (from the route path), hreflang and Open Graph. Do not put a static canonical in `nuxt.config.ts`. Site-wide `Organization`/`Store`/`WebSite` JSON-LD is in `app.vue`, the catalog `ItemList` in `pages/index.vue`, `Product` + `Offer` (UAH) in `pages/products/[id].vue`. Admin/transactional pages use `noindex: true`.
- Unknown product slugs must return a real 404 (`createError({ statusCode: 404, fatal: true })`); old ids redirect with 301 to the slug URL.
- `app.vue` renders `<NuxtPage />` once. Do not add `<router-view>` next to it (it duplicates every page).
- The catalog lives at `/` (`pages/index.vue`); product pages at `/products/<slug>` (`pages/products/[id].vue`); `/products` only 301-redirects to `/`. UI text is Ukrainian.

### Docker / environment
- `docker-compose.yml` = local (localhost URLs, no CDN). `docker-compose.prod.yml` = VPS (127.0.0.1 ports, production URLs from `.env`). Keep them in sync when adding services or variables.
- The frontend service sets `NUXT_API_BASE_INTERNAL=http://backend:8000` in both compose files (SSR talks to the backend over the Docker network). `NUXT_SITE_URL` (optional, default `https://natur-savon.com.ua`) is the canonical origin for SEO tags and the sitemap.
- A single root `.env` is used. Do not create `app/.env` (it would be baked into the image). `.env` is secret: never print, log or commit its values; add new keys to `.env.example` instead.
- Postgres credentials only apply when the volume is first created; changing them later requires `down -v` (local) or `ALTER USER` (server).

## Gotchas
- Local `npm run build` needs Node 20+ (Vite 7); Node 18 fails with `crypto.hash is not a function`. Build through Docker (`docker compose up -d --build frontend`).
- Compression: Nuxt pre-compresses static assets (`nitro.compressPublicAssets`, gzip + brotli) but does not compress SSR HTML. On the VPS nginx listens on port 80 only (Cloudflare terminates TLS/HTTP2/3) and compresses HTML; `/etc/nginx/conf.d/compression.conf` (not in the repo) adds `gzip_vary`, `gzip_proxied any`, `gzip_types`, etc. Do not repeat `gzip on;` there, it is already in `nginx.conf` and a duplicate fails `nginx -t`. Cloudflare Rocket Loader / Auto Minify should stay off.
- Deploying image changes: rebuild backend + frontend, `cd cloudflare-worker && npx wrangler deploy`, then run `python one_time_images_optimization_script.py` (`--dry-run` first) once to create variants for images uploaded earlier. Standard Cloudflare has no resizing; paid Cloudflare Images / Image Resizing (`cf.image`) could replace the variant files later.
- `create_admin.py` deletes and recreates the admin on each start.
- nginx on the VPS caches HTML (`/etc/nginx/sites-enabled/natur-savon`, `location /`, `proxy_cache_valid 200 302 1m`), separately per `Accept-Encoding` variant. After every deploy, once backend and frontend are up, purge it: `sudo find /var/cache/nginx -type f -delete && sudo nginx -s reload`. Otherwise a page rendered while the backend was still starting (empty catalog) can be served from cache. Verify with `curl -s https://natur-savon.com.ua/ | grep -c 'class="product-card"'`.
- Cart uses an anonymous `Session-ID` header (UUID); `/cart/add/{id}` accepts GET and POST.
- `GET /product/types/` is public; flavours, create/update/delete and image delete/reorder require admin.
- The browser uploads images directly to S3 (presigned PUT); the bucket CORS must allow the site origins.
- The old `frontend/router.options.ts` is not used by Nuxt 3 at this location; do not rely on it.
- Terminal heredocs are fragile in this environment; for multi-line file writes prefer the editor tools.

