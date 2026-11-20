# SSR + GEO/SEO Setup Runbook (Nuxt 3 + API + NGINX + Cloudflare)

Instructions for an AI coding/ops agent to make a Nuxt 3 shop/catalog site readable by crawlers and LLMs (content in the **raw HTML**), with correct per-page SEO and structured data. Pair it with `browser_caching_setup_guide_for_ai_agents.md` for NGINX/Cloudflare caching.

Replace the placeholders:
- `<DOMAIN>`: primary domain (e.g., `example.com`)
- `<API_INTERNAL>`: API URL reachable from the frontend container (e.g., `http://backend:8000`)
- `<API_PUBLIC>`: public API URL used by the browser (e.g., `https://api.<DOMAIN>`)
- `<LANG>` / `<LOCALE>`: e.g., `uk` / `uk_UA`; `<CURRENCY>`: e.g., `UAH`

---

## Problem Statement

If pages load data in `onMounted`, the server HTML contains no catalog/product content. Crawlers and LLMs (and "rendering percentage" audits) see an empty shell. Goal: public content is in the initial HTML; per-visitor state stays client-only.

## Step 1: Audit

1. `curl -s https://<DOMAIN>/ | grep -c '<product-marker>'` (use a class that exists once per item, e.g. `class="product-card"`). `0` means client-only rendering.
2. List where data is fetched: `grep -rn "onMounted\|useFetch\|\$fetch" pages components`.
3. Check `nuxt.config.ts` for a static `canonical` / `hreflang` (wrong: every route points to the root).
4. Check `public/robots.txt` exists, allows crawlers, disallows only admin/transactional routes, and links the sitemap.

## Step 2: SSR-safe data loading

Rules:
- Public data: `await useAsyncData(key, () => $fetch(...))` in `<script setup>`. The payload is serialized and reused on the client (no refetch on hydration). Use a unique `key` per route param (e.g. `` `product-${slug}` ``).
- Click handlers / `onMounted`: plain `$fetch`. Avoid `useFetch` (caches by URL).
- Per-visitor state (cart, session id, admin token): load only in `onMounted`; guard `localStorage`, `crypto`, `window` with `import.meta.client`. Never render this state on the server.
- Do not swallow fetch errors silently (`.catch(() => [])` produces an empty cached page). Log with `console.error` and retry once.
- Unknown slug: `throw createError({ statusCode: 404, fatal: true })`. Old id URLs: `navigateTo(newUrl, { redirectCode: 301 })`.
- Define helper functions **before** the `useAsyncData` callback that uses them (arrow `const` is not hoisted).

### SSR must use the internal API URL

Inside Docker, `localhost` / the public hostname may be unreachable from the frontend container. Add a server-only runtime config and a composable:

```ts
// nuxt.config.ts → runtimeConfig
apiBaseInternal: process.env.NUXT_API_BASE_INTERNAL || '',   // private, server only
public: { apiBase: process.env.NUXT_PUBLIC_API_BASE || '', siteUrl: (process.env.NUXT_SITE_URL || 'https://<DOMAIN>').replace(/\/$/, '') }
```

```ts
// composables/useApiBase.ts
export const useApiBase = (): string => {
  const config = useRuntimeConfig();
  if (import.meta.server && config.apiBaseInternal) return String(config.apiBaseInternal).replace(/\/$/, '');
  return String(config.public.apiBase).replace(/\/$/, '');
};
```

Set `NUXT_API_BASE_INTERNAL=<API_INTERNAL>` in **every** compose file (local and prod). Capture `const apiBase = useApiBase()` in setup; it is correct on the server and again on the client.

## Step 3: Per-page SEO composable

Create `composables/usePageSeo.ts` taking `{ title, description, image?, noindex? }` (or a getter). It sets `<title>`, meta description, `robots`, canonical built from `siteUrl + route.path` (no query string), hreflang, and Open Graph (`og:title`, `og:description`, `og:url`, `og:image`, `og:locale`). Call it on every page. Admin/transactional pages pass `noindex: true`. Remove static canonical/hreflang from `nuxt.config.ts`. `siteUrl` must be in `runtimeConfig.public`, otherwise client-side navigation loses it.

## Step 4: JSON-LD (schema.org)

Use `useHead({ script: [{ key, type: 'application/ld+json', innerHTML: JSON.stringify(obj) }] })` (a unique `key` prevents duplicates).
- `app.vue`: `@graph` with `Organization`+`Store` (name, url, logo, description, `sameAs` social links, `areaServed`, `currenciesAccepted`) and `WebSite` (`inLanguage`).
- Catalog page: `ItemList` with `ListItem` url/name per product.
- Product page: `Product` (name, description, sku, images, category, brand, weight as `QuantitativeValue`, `material` for ingredients, `additionalProperty` for characteristics) with `Offer` (`price`, `priceCurrency: <CURRENCY>`, `availability`, `itemCondition`, `seller`). Use absolute URLs.
- Sitemap: a server route (`server/routes/sitemap.xml.ts`) listing static pages + every product URL, built from `siteUrl`.

## Step 5: Backend gotchas that break SSR data

- Missing DB columns make list endpoints return 500 (`column ... does not exist`) and the SSR catalog silently empties. `create_all` never alters existing tables: add idempotent `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` for every model column added later (run at container start).
- Make the frontend wait for the API: `depends_on` the backend (ideally with a healthcheck) so SSR does not render before the API is ready.

## Step 6: Deploy and verify

```bash
docker compose -f docker-compose.prod.yml up -d --build backend frontend
sleep 10
sudo find /var/cache/nginx -type f -delete && sudo nginx -s reload   # purge cached HTML
```

Checks (raw HTML, no JS):

```bash
curl -s https://<DOMAIN>/ | grep -c '<product-marker>'                          # > 0
curl -s https://<DOMAIN>/ | grep -oE '<title>[^<]*|<link rel="canonical"[^>]*|application/ld\+json'
curl -s https://<DOMAIN>/products/<slug> | grep -oE '<title>[^<]*|<link rel="canonical"[^>]*|"@type":"Offer"[^}]*'
curl -s -o /dev/null -w '%{http_code}\n' https://<DOMAIN>/products/does-not-exist   # 404
docker exec <frontend-container> printenv NUXT_API_BASE_INTERNAL
```

Also compare with Cloudflare-like headers: `curl -s -H 'Host: <DOMAIN>' -H 'Accept-Encoding: br, gzip' http://127.0.0.1/ | grep -c '<product-marker>'`.

## Troubleshooting Reference

| Symptom | Cause | Fix |
|---|---|---|
| Public site shows 0 items, `127.0.0.1:<port>` shows many | NGINX HTML cache holds a page rendered while the API was down; cached per `Accept-Encoding` variant (`X-Proxy-Cache: HIT`) | Purge `/var/cache/nginx` + reload; set HTML `proxy_cache_valid` to `1m`; purge after every deploy. |
| SSR catalog empty, API fine from host | Frontend container cannot reach the API URL used on the server | Set `NUXT_API_BASE_INTERNAL` and use `useApiBase()`. |
| API list endpoint 500 after a model change | Existing DB lacks the new columns | Add `ADD COLUMN IF NOT EXISTS` migrations at startup. |
| All pages share one canonical | Static canonical in `nuxt.config.ts` | Use `usePageSeo()`, remove the static link. |
| Canonical/JSON-LD URL is `undefined` after navigation | `siteUrl` only in private runtime config | Put `siteUrl` in `runtimeConfig.public`. |
| `compose up --build` fails with "invalid environment variable" | Stray non-`KEY=value` line in `.env` | Remove it (never print `.env` values). |
| Edits to one file silently lost | Several parallel edits to the same file | Apply edits to one file sequentially and re-read it. |
| Hash/credentials in logs | Startup script prints secrets | Remove the `print` of password hashes. |

