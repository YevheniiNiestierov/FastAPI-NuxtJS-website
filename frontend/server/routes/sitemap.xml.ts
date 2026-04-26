import { defineEventHandler, setResponseHeader } from 'h3';

const SITE_URL = process.env.NUXT_SITE_URL || 'https://natur-savon.com.ua';
const API_BASE = process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000';

// Static pages that should always be in the sitemap
// Excluded: /login, /order, /manager (private/functional, blocked in robots.txt too)
const staticPages = [
  { loc: '/products', priority: '1.0', changefreq: 'daily' },
  { loc: '/about', priority: '0.7', changefreq: 'monthly' },
  { loc: '/contract', priority: '0.5', changefreq: 'yearly' },
];

export default defineEventHandler(async (event) => {
  setResponseHeader(event, 'Content-Type', 'application/xml');
  setResponseHeader(event, 'Cache-Control', 'public, max-age=3600'); // cache 1h

  // Fetch all products from FastAPI
  let products: Array<{ id: number | string }> = [];
  try {
    const data = await $fetch<Array<{ id: number | string }>>(`${API_BASE}/product/products`);
    if (Array.isArray(data)) {
      products = data;
    }
  } catch (e) {
    console.error('[sitemap] Failed to fetch products:', e);
  }

  const today = new Date().toISOString().split('T')[0];

  const staticEntries = staticPages
    .map(
      (p) => `
  <url>
    <loc>${SITE_URL}${p.loc}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${p.changefreq}</changefreq>
    <priority>${p.priority}</priority>
  </url>`
    )
    .join('');

  const productEntries = products
    .map(
      (p) => `
  <url>
    <loc>${SITE_URL}/products/${p.id}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>`
    )
    .join('');

  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${staticEntries}
${productEntries}
</urlset>`;
});

