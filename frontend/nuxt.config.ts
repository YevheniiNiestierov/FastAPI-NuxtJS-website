import { defineNuxtConfig } from 'nuxt/config';

export default defineNuxtConfig({
  runtimeConfig: {
    components: true,
    siteUrl: process.env.NUXT_SITE_URL || 'https://natur-savon.com.ua',
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
      cdnBase: (process.env.NUXT_PUBLIC_CDN_BASE || '').replace(/\/$/, '')
    }
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
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { rel: 'canonical', href: 'https://natur-savon.com.ua' },
        // 4. Hreflang usage
        { rel: 'alternate', hreflang: 'uk-UA', href: 'https://natur-savon.com.ua' }
      ]
    }
  },
  devtools: {enabled: true},
  server: {
    port: process.env.PORT || 3000,
    host: process.env.HOST || '0.0.0.0'
  }
});