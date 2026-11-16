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
      htmlAttrs: {
        lang: 'uk'
      },
      title: 'Natur Savon — Натуральне мило та косметика ручної роботи',
      meta: [
        { name: 'description', content: 'Купити натуральне мило ручної роботи та органічну косметику Natur Savon в Україні. Широкий асортимент, приємні ціни, швидка доставка. Замовляйте онлайн!' },
        { name: 'google-site-verification', content: 'eaxm-8wm8qc-A7l_Vny5YyO6UBpx88uVjynYIsKBn7M' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { rel: 'canonical', href: 'https://natur-savon.com.ua' },
        { rel: 'alternate', hreflang: 'uk', href: 'https://natur-savon.com.ua' },
        { rel: 'alternate', hreflang: 'x-default', href: 'https://natur-savon.com.ua' }
      ]
    }
  },
  devtools: { enabled: true },
  server: {
    port: process.env.PORT || 3000,
    host: process.env.HOST || '0.0.0.0'
  }
});
```

---

### 2. Update `index.vue` (Product Grid Page)

In your `index.vue`, we need to add an `<h1>` header tag. Since your logo section sits at the top, you can include an SEO-friendly `<h1>` tag right inside the brand section (or styled with `.visually-hidden` if you prefer it hidden from visual layout while remaining fully readable by search engine crawlers).

Here is the updated template snippet for `index.vue`[cite: 3]:

```html
<template>
  <div class="store-wrapper">
    <header class="store-header">
      <nav class="header-nav">
        <NuxtLink to="/about" class="nav-link">Про нас</NuxtLink>
        <NuxtLink to="/contract" class="nav-link">Публічний договір</NuxtLink>
      </nav>
      <NuxtLink v-if="isAdmin" to="/manager" class="admin-link">Панель менеджера</NuxtLink>
    </header>

    <section class="brand-section">
      <img
        src="/natur_savon_logo.webp"
        alt="Natur Savon Logo"
        width="250"
        height="250"
        fetchpriority="high"
        decoding="async"
        class="brand-image"
      />
      <!-- H1 Header Tag for SEO & Heading Hierarchy -->
      <h1 class="visually-hidden">Natur Savon — Натуральне мило та косметика ручної роботи</h1>
    </section>

    <main class="main-content">
      <!-- Filters and Product Grid -->
      <section class="type-filter">
        <button
          class="filter-btn"
          :class="{ active: selectedType === null }"
          @click="selectedType = null"
        >Всі</button>
        <button
          v-for="type in productTypes"
          :key="type"
          class="filter-btn"
          :class="{ active: selectedType === type }"
          @click="selectedType = type"
        >{{ type }}</button>
      </section>

      <section class="products-section">
        <div class="product-grid">
          <div v-for="(product, idx) in filteredProducts" :key="product.id" class="product-card" @mouseenter="product.hovered = true">
            <div class="image-container">
              <NuxtLink :to="`/products/${product.slug || product.id}`" class="image-link">
                <img
                  v-if="product.imageUrl"
                  :src="product.imageUrl"
                  :alt="product.title"
                  :loading="idx < 4 ? 'eager' : 'lazy'"
                  :fetchpriority="idx < 4 ? 'high' : 'auto'"
                  decoding="async"
                  class="product-image product-image--base"
                />
                <img
                  v-if="product.hoverImageUrl && product.hovered"
                  :src="product.hoverImageUrl"
                  :alt="product.title"
                  loading="lazy"
                  decoding="async"
                  class="product-image product-image--hover"
                />
              </NuxtLink>
            </div>
            <div class="product-info">
              <!-- Product titles act as H2 tags, perfectly following the H1 above -->
              <h2 class="product-title">{{ product.title }}</h2>
              <p class="product-description">{{ product.description }}</p>

              <div class="product-meta">
                <span class="product-weight">{{ product.weight }} г.</span>
                <span class="product-price">{{ product.price }} ₴</span>
              </div>

              <div class="product-actions">
                <div class="quantity-controls">
                  <div class="qty-controls">
                    <button type="button" class="qty-btn" @click="product.quantity = Math.max(1, product.quantity - 1)">−</button>
                    <input type="number" v-model.number="product.quantity" min="1" class="quantity-input" />
                    <button type="button" class="qty-btn" @click="product.quantity++">+</button>
                  </div>
                </div>
                <button @click="addItemToCart(product)" class="btn-primary">
                  Додати
                </button>
              </div>
              <NuxtLink :to="`/products/${product.slug || product.id}`" class="details-link">Детальніше про товар</NuxtLink>
            </div>
          </div>
        </div>
      </section>
    </main>

    <div class="cart-wrapper">
      <theCart />
    </div>
  </div>
</template>
```[cite: 3]

Add the helper CSS class `.visually-hidden` to your `<style scoped>` block in `index.vue`[cite: 3] if you want the H1 to remain hidden visually while fully readable by search engine crawlers:

```css
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}