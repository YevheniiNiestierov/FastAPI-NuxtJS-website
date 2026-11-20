import { defineNuxtConfig } from 'nuxt/config';

export default defineNuxtConfig({
  runtimeConfig: {
    components: true,
    siteUrl: process.env.NUXT_SITE_URL || 'https://natur-savon.com.ua',
    // Server-only API URL for SSR fetches (e.g. http://backend:8000 inside Docker). Empty = use public.apiBase.
    apiBaseInternal: process.env.NUXT_API_BASE_INTERNAL || '',
    public: {
      siteUrl: (process.env.NUXT_SITE_URL || 'https://natur-savon.com.ua').replace(/\/$/, ''),
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
      cdnBase: (process.env.NUXT_PUBLIC_CDN_BASE || '').replace(/\/$/, '')
    }
  },
  // Static files from /public are not fingerprinted, so cache them for 30 days (not "immutable").
  // /_nuxt/* is fingerprinted and already served as immutable by Nuxt.
  routeRules: {
    '/natur_savon_logo*.webp': { headers: { 'Cache-Control': 'public, max-age=2592000' } },
    '/background_image.webp': { headers: { 'Cache-Control': 'public, max-age=2592000' } }
  },
  // Critical CSS is tiny (~9 KB total) and Nuxt already inlines it into the SSR HTML
  // (entry + page + component styles). Nuxt still adds <link rel="stylesheet"> tags for the same files,
  // which are render-blocking duplicates, so they are removed from the SSR render below.
  features: {
    inlineStyles: true
  },
  hooks: {
    'build:manifest': (manifest) => {
      for (const key in manifest) {
        const file = manifest[key];
        if (file.resourceType === 'style') {
          file.preload = false;
          file.prefetch = false;
        }
        file.css = [];
      }
    }
  },
  // Pre-compress static assets at build time (gzip + brotli); served when the client sends Accept-Encoding.
  nitro: {
    compressPublicAssets: { gzip: true, brotli: true }
  },
  app: {
    head: {
      // 1. Lang attribute for the HTML tag
      htmlAttrs: {
        lang: 'uk' // Assuming Ukrainian based on the domain and UI text
      },
      // 2. Global Title Tag
      title: 'Natur Savon - Натуральне мило та косметика ручної роботи',
      meta: [
        { name: 'google-site-verification', content: 'eaxm-8wm8qc-A7l_Vny5YyO6UBpx88uVjynYIsKBn7M' },
        // 3. Meta Description
        {
          name: 'description',
          content: 'Купити натуральне мило та косметику ручної роботи від Natur Savon. Широкий асортимент екологічних товарів для догляду за шкірою за доступними цінами.'
        }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
        // canonical / hreflang are set per page via usePageSeo()
      ]
    }
  },
  devtools: {enabled: true},
  server: {
    port: process.env.PORT || 3000,
    host: process.env.HOST || '0.0.0.0'
  }
});