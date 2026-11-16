// Dynamic sitemap: static pages + every product from the API.
const STATIC_PATHS = ['/', '/about', '/contract', '/privacy-policy'];

const escapeXml = (value: string) =>
  value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig(event);
  const baseUrl = config.siteUrl.replace(/\/$/, '');

  let productPaths: string[] = [];
  try {
    const products = await $fetch<Array<{ id: string | number; slug?: string | null }>>(
      `${config.public.apiBase}/product/products`
    );
    productPaths = products.map(p => `/products/${p.slug || p.id}`);
  } catch (error) {
    console.error('Sitemap: failed to load products', error);
  }

  const urls = [...STATIC_PATHS, ...productPaths]
    .map(path => `  <url>\n    <loc>${escapeXml(baseUrl + path)}</loc>\n  </url>`)
    .join('\n');

  setHeader(event, 'Content-Type', 'application/xml; charset=utf-8');
  setHeader(event, 'Cache-Control', 'public, max-age=3600');

  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`;
});


