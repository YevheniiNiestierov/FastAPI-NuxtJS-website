# Browser Caching Setup Runbook (NGINX + Nuxt 3 + Cloudflare)

Instructions for an AI coding/ops agent to configure long-lived browser caching (`Cache-Control`) on a VPS running **NGINX**, **Nuxt 3** (Docker), **Cloudflare Tunnel (`cloudflared`)**, and an optional **Cloudflare Worker** for images.

Replace the placeholders before running:
- `<DOMAIN>`: primary domain (e.g., `example.com`)
- `<SITE_SLUG>`: short unique identifier for filenames and cache zones (e.g., `my_shop`)
- `<FRONTEND_PORT>`: local Nuxt container port (default `3000`)
- `<BACKEND_PORT>`: local API container port (default `8000`, if applicable)

---

## Target Caching Policy

| Asset Type | Location / Origin | `Cache-Control` Header | Reason |
|---|---|---|---|
| Hashed Nuxt bundles (`/_nuxt/*`) | NGINX → Nuxt | `public, max-age=31536000, immutable` | Content-hashed filenames; safe to cache 1 year. |
| Unhashed static assets (`.ico`, `.png`, `.webp`, `.svg`, `.woff2`, etc.) | NGINX → Nuxt | `public, max-age=2592000` | 30 days; unhashed files must not be `immutable`. |
| HTML / SSR routes (`/`) | NGINX → Nuxt | Default (no long browser cache); nginx server-side cache 1 minute | Prevents browsers from trapping stale HTML; a short TTL limits stale SSR content (purge `/var/cache/nginx` after each deploy). |
| Versioned CDN images (`?v=<ver>`) | Cloudflare Worker | `public, max-age=31536000, immutable` | Version query string busts cache on update. |

---

## Step 1: Audit the Current Server Setup

Run these read-only checks first to avoid conflicts with existing sites on the same VPS:

```bash
# 1. Confirm container ports
docker ps

# 2. Check existing NGINX sites and cache zones (avoid duplicate keys_zone names)
ls -la /etc/nginx/sites-enabled/
grep -rn "proxy_cache_path" /etc/nginx/

# 3. Check if Cloudflare Tunnel (cloudflared) is running
ps aux | grep -iE 'cloudflared|caddy|traefik'

# 4. Check what is listening on ports 80 and 443
ss -tlnp | grep -E ':80|:443'
```

---

## Step 2: Configure NGINX

Create or update `/etc/nginx/sites-available/<SITE_SLUG>` and symlink it into `/etc/nginx/sites-enabled/`.

### Critical Rules
1. **Include both IPv4 and IPv6 (`listen 80;` and `listen [::]:80;`)**: `cloudflared` connecting to `http://localhost:80` resolves `localhost` to IPv6 (`::1`) first on Ubuntu. Without `listen [::]:80;`, NGINX's `default` site intercepts the request and returns `404`.
2. **Unique `proxy_cache_path` and `keys_zone`**: Never declare the same cache directory or `keys_zone` name twice across NGINX configs, or `nginx -t` will fail.
3. **Strip upstream `Cache-Control` before setting new ones**: Use `proxy_hide_header Cache-Control;` before `add_header Cache-Control ...;` to avoid duplicate headers.

### NGINX Site Template (`/etc/nginx/sites-available/<SITE_SLUG>`)

```nginx
proxy_cache_path /var/cache/nginx/<SITE_SLUG> levels=1:2 keys_zone=<SITE_SLUG>_cache:10m max_size=1g inactive=60m use_temp_path=off;

server {
    listen 80;
    listen [::]:80;
    server_name <DOMAIN> www.<DOMAIN>;

    # 1. Nuxt hashed bundles (JS, CSS, chunks) — 1 year immutable
    location /_nuxt/ {
        proxy_pass http://127.0.0.1:<FRONTEND_PORT>;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_cache <SITE_SLUG>_cache;
        proxy_cache_valid 200 30d;

        proxy_hide_header Cache-Control;
        add_header Cache-Control "public, max-age=31536000, immutable";
        add_header X-Proxy-Cache $upstream_cache_status;
    }

    # 2. Unhashed static files (favicon, fonts, local images) — 30 days
    location ~* \.(?:ico|gif|jpe?g|png|webp|svg|woff2?|ttf|eot)$ {
        proxy_pass http://127.0.0.1:<FRONTEND_PORT>;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_cache <SITE_SLUG>_cache;
        proxy_cache_valid 200 7d;

        proxy_hide_header Cache-Control;
        add_header Cache-Control "public, max-age=2592000";
        add_header X-Proxy-Cache $upstream_cache_status;
    }

    # 3. HTML / SSR pages — short server-side cache, no long browser cache
    location / {
        proxy_pass http://127.0.0.1:<FRONTEND_PORT>;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_cache <SITE_SLUG>_cache;
        proxy_cache_valid 200 302 10m;
        proxy_cache_valid 404 1m;

        add_header X-Proxy-Cache $upstream_cache_status;
    }
}

# Optional: API subdomain (no caching)
server {
    listen 80;
    listen [::]:80;
    server_name api.<DOMAIN>;

    location / {
        proxy_pass http://127.0.0.1:<BACKEND_PORT>;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable, validate, and reload NGINX:

```bash
ln -sf /etc/nginx/sites-available/<SITE_SLUG> /etc/nginx/sites-enabled/<SITE_SLUG>
nginx -t && systemctl reload nginx
```

Verify NGINX directly (bypassing Cloudflare):

```bash
curl -I -H "Host: <DOMAIN>" http://127.0.0.1/favicon.ico
```

Expected headers:
- `HTTP/1.1 200 OK`
- `Cache-Control: public, max-age=2592000`
- `X-Proxy-Cache: MISS` (then `HIT` on repeat)

---

## Step 3: Cloudflare Dashboard Configuration

Ask the user to perform (or automate via Cloudflare API) these three settings:

1. **Route Tunnel through NGINX (if using `cloudflared`)**:
   - Go to **Cloudflare Dashboard → Networking → Tunnels** (or Connectors → Cloudflare Tunnels) → select tunnel → **Routes**.
   - Edit the route for `<DOMAIN>` (and `www.<DOMAIN>` if present).
   - Change **Service** from `http://localhost:<FRONTEND_PORT>` to `http://localhost:80` so requests pass through NGINX.
   - Leave `api.<DOMAIN>` pointing to `http://localhost:<BACKEND_PORT>` (or `http://localhost:80`).
2. **Preserve Origin Cache Headers**:
   - Go to **Caching → Configuration → Browser Cache TTL**.
   - Set to **Respect Existing Headers** (otherwise Cloudflare overrides headers with its default 4-hour `max-age=14400`).
3. **Purge Edge Cache**:
   - Click **Purge Everything** under **Caching → Configuration** so Cloudflare drops any old cached responses.

---

## Step 4: Verify Cloudflare Worker Image Caching (If Applicable)

If product/media images are served through a Cloudflare Worker from S3/R2:
- Versioned URLs (containing `?v=<timestamp-or-hash>`) must set:
  `Cache-Control: public, max-age=31536000, immutable`
- Unversioned URLs should use a shorter TTL:
  `Cache-Control: public, max-age=3600`
- Non-200 responses (`404`, `5xx`) must never be cached:
  `Cache-Control: no-store`

---

## Step 5: End-to-End Verification

Run these checks from the VPS after Cloudflare changes are saved and purged:

```bash
# 1. Verify static asset caching
curl -I https://<DOMAIN>/favicon.ico
# Expect: HTTP/2 200, cache-control: public, max-age=2592000, x-proxy-cache: HIT/MISS

# 2. Verify Nuxt hashed bundle caching
BUNDLE=$(curl -sL https://<DOMAIN>/ | grep -oE '/_nuxt/[^"]+\.(js|css)' | head -n 1)
curl -I "https://<DOMAIN>${BUNDLE}"
# Expect: HTTP/2 200, cache-control: public, max-age=31536000, immutable, x-proxy-cache: HIT/MISS
```

---

## Troubleshooting Reference

| Symptom | Cause | Fix |
|---|---|---|
| `nginx -t` fails with duplicate zone/path | `proxy_cache_path` or `keys_zone` already defined | Use a unique path (`/var/cache/nginx/<SITE_SLUG>`) and `keys_zone` name. |
| `cache-control: max-age=14400` | Cloudflare Browser Cache TTL overriding origin | Set **Browser Cache TTL** to **Respect Existing Headers** and purge cache. |
| `x-proxy-cache` missing over HTTPS, present on `127.0.0.1` | Cloudflare Tunnel points to `:3000` instead of `:80` | Point the Tunnel route for `<DOMAIN>` to `http://localhost:80`. |
| `HTTP/2 404` right after pointing Tunnel to `localhost:80` | `localhost` resolves to IPv6 `::1`, hitting NGINX `default` site | Add `listen [::]:80;` to the `<DOMAIN>` NGINX `server` block and reload. |
| Old headers still showing after fix (`cf-cache-status: HIT`, high `age:`) | Stale response in Cloudflare edge cache | Test with `?v=test` to verify origin, then **Purge Everything** in Cloudflare. |