import { defineNuxtConfig } from 'nuxt/config';

export default defineNuxtConfig({
  runtimeConfig: {
    components: true,
    siteUrl: process.env.NUXT_SITE_URL || 'https://natur-savon.com.ua',
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000'
    }
  },
  app: {
    head: {
      meta: [
        { name: 'google-site-verification', content: 'eaxm-8wm8qc-A7l_Vny5YyO6UBpx88uVjynYIsKBn7M' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { rel: 'canonical', href: 'https://natur-savon.com.ua' }
      ]
    }
  },
  devtools: {enabled: true},
  server: {
    port: process.env.PORT || 3000,
    host: process.env.HOST || '0.0.0.0'
  }
});
