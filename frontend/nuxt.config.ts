import { defineNuxtConfig } from 'nuxt/config';

export default defineNuxtConfig({
  runtimeConfig: {
    components: true,
    public: {
      apiBase: 'http://localhost:8000'
    }
  },
  devtools: {enabled: true}
});
