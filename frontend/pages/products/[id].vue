<template>
  <div class="page-wrapper">
    <div v-if="pending && !product" class="loading">
      Завантаження...
    </div>

    <div v-else-if="product">
      <NuxtLink to="/products" class="back-link">
        <span class="arrow">←</span> Назад до магазину
      </NuxtLink>

      <div class="product-container">
        <!-- Left: Image Gallery -->
        <div class="image-section">
          <div class="main-image-wrapper">
            <img :src="mainImageUrl" :alt="product.title" class="product-image" :style="{ opacity: imageVisible ? 1 : 0 }" />
          </div>
          <div v-if="imageGallery.length > 1" class="thumbnail-gallery">
            <img
              v-for="imageKey in imageGallery"
              :key="imageKey"
              :src="getThumbnailUrl(imageKey)"
              :alt="`Thumbnail for ${product.title}`"
              @click="setActiveImage(imageKey)"
              :class="{ active: activeImageKey === imageKey }"
              class="thumbnail-image"
            />
          </div>
          <p v-if="product.description" class="product-desc">{{ product.description }}</p>
        </div>

        <!-- Right: Product Info -->
        <div class="info-section">
          <div class="product-header-row-vertical">
            <h1 class="product-title">{{ product.title }}</h1>
            <div class="product-meta">
              <p class="price"><span>{{ product.price }} грн.</span></p>
              <p class="weight">Вага: {{ product.weight }} г.</p>
            </div>
            <div class="quantity-wrapper">
              <label for="qty">Кількість:</label>
              <div class="qty-controls">
                <button @click="selectedQuantity = Math.max(1, selectedQuantity - 1)" class="qty-btn">−</button>
                <input
                  id="qty"
                  type="number"
                  v-model.number="selectedQuantity"
                  min="1"
                  class="quantity-input"
                />
                <button @click="selectedQuantity++" class="qty-btn">+</button>
              </div>
            </div>
          </div>

          <div class="actions">
            <button @click="addItemToCart" class="add-to-cart-button">
              Купити
            </button>
          </div>


          <div v-if="product.instructions" class="product-instructions">
            <h3 class="instructions-title">Інструкція із застосування</h3>
            <p class="instructions-text">{{ product.instructions }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="cart-wrapper">
      <theCart />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed, watch } from "vue";
import { useRoute, useRuntimeConfig, useState } from "#app";

// Config & Route
const config = useRuntimeConfig();
const route = useRoute();

// State
const product = ref(null);
const selectedQuantity = ref(1);
const sessionID = ref(null);
const pending = ref(true);
const imageGallery = ref([]);
const activeImageKey = ref('');

// Global State (Shared with Cart)
const productsInCart = useState('productsInCart', () => []);
const totalPrice = useState('totalPrice', () => 0);

// Computed Image URL — served directly from Cloudflare CDN (no FastAPI redirect).
// activeImageKey stores the full CDN URL of the currently displayed image.
const mainImageUrl = computed(() => activeImageKey.value || '');

// Thumbnails also point directly to the CDN URL stored in imageGallery items.
const getThumbnailUrl = (cdnUrl) => cdnUrl || '';

const imageVisible = ref(true);

const setActiveImage = (key) => {
  if (key === activeImageKey.value) return;
  imageVisible.value = false;
  setTimeout(() => {
    activeImageKey.value = key;
    imageVisible.value = true;
  }, 200);
};

const fetchProduct = async (id) => {
  pending.value = true;
  try {
    product.value = await $fetch(`${config.public.apiBase}/product/products/${id}`);
    await fetchImageGallery();
  } catch (error) {
    console.error('Error fetching product:', error);
  } finally {
    pending.value = false;
  }
};

const fetchImageGallery = async () => {
  if (!product.value?.title) return;
  try {
    const encodedTitle = encodeURIComponent(product.value.title);
    // Gallery now returns: [{ key: string, cdn_url: string }, ...]
    const data = await $fetch(`${config.public.apiBase}/image/images/gallery/${encodedTitle}`);
    if (data && data.length > 0) {
      // imageGallery stores cdn_urls; activeImageKey holds the currently shown cdn_url
      imageGallery.value = data.map(item => item.cdn_url).filter(Boolean);
      activeImageKey.value = imageGallery.value[0] || '';
    } else {
      const fallbackUrl = config.public.cdnBase
        ? `${config.public.cdnBase}/${encodeURIComponent(product.value.title)}_1.webp`
        : '';
      imageGallery.value = fallbackUrl ? [fallbackUrl] : [];
      activeImageKey.value = fallbackUrl;
    }
  } catch {
    const fallbackUrl = config.public.cdnBase
      ? `${config.public.cdnBase}/${encodeURIComponent(product.value.title)}_1.webp`
      : '';
    imageGallery.value = fallbackUrl ? [fallbackUrl] : [];
    activeImageKey.value = fallbackUrl;
  }
};

const addItemToCart = async () => {
  if (!sessionID.value) return;
  try {
    const pid = product.value.product_id || product.value.id;
    await $fetch(`${config.public.apiBase}/cart/add/${pid}`, {
      method: 'POST',
      headers: { 'Session-ID': sessionID.value },
      params: { quantity: selectedQuantity.value }
    });
    await fetchProductsAndTotalSum();
    alert(`Товар "${product.value.title}" додано до кошика!`);
  } catch (error) {
    console.error('Error adding product to basket:', error);
  }
};

const fetchProductsAndTotalSum = async () => {
  try {
    const data = await $fetch(`${config.public.apiBase}/cart/cart-products-and_total-price`, {
      headers: { 'Session-ID': sessionID.value }
    });
    if (data) {
      if (Array.isArray(data)) {
        productsInCart.value = data[0] || [];
        totalPrice.value = data[1] || 0;
      } else {
        productsInCart.value = data.products || [];
        totalPrice.value = data.total_sum || 0;
      }
    }
  } catch (error) {
    console.error('Error fetching products in cart:', error);
  }
};

onMounted(async () => {
  // Session Management
  let storedSession = localStorage.getItem('sessionID');
  if (!storedSession) {
    storedSession = crypto.randomUUID();
    localStorage.setItem('sessionID', storedSession);
  }
  sessionID.value = storedSession;

  const id = route.params.id || window.location.pathname.split('/').filter(Boolean).pop();
  if (id) {
    await fetchProduct(id);
  }
  await fetchProductsAndTotalSum();
});

// Re-fetch when navigating between products without a full page reload
watch(() => route.params.id, async (newId) => {
  if (!newId) return;
  product.value = null;
  imageGallery.value = [];
  activeImageKey.value = '';
  await fetchProduct(newId);
});
</script>

<style scoped>
.page-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading {
  text-align: center;
  font-size: 1.2rem;
  padding: 50px;
  color: #666;
}

/* Back link */
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  color: #753BBD;
  text-decoration: none;
  margin-bottom: 16px;
}
.back-link:hover { text-decoration: underline; }
.arrow { font-size: 1rem; }

/* 2-Column Layout */
.product-container {
  display: flex;
  gap: 0;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  overflow: hidden;
  align-items: stretch; /* stretch both columns to equal height */
  min-height: 0;
}

/* Left Column — image */
.image-section {
  flex: 0 0 50%;
  max-width: 50%;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: #f5edfa; /* washed purple */
  padding: 20px;
  box-sizing: border-box;
  min-height: 100%;
  height: auto;
}

.main-image-wrapper {
  width: 100%;
  aspect-ratio: 1 / 1;
  overflow: hidden;
  border-radius: 6px;
  /* Remove background and border */
  background: none;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: opacity 0.25s ease;
}

.thumbnail-gallery {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}

.thumbnail-image {
  width: 70px;
  height: 70px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.2s;
}
.thumbnail-image:hover { border-color: #ccc; }
.thumbnail-image.active { border-color: #753BBD; }

/* Right Column — info */
.info-section {
  flex: 0 0 50%;
  max-width: 50%;
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 30px 32px;
  box-sizing: border-box;
  min-height: 100%;
  height: auto;
}

.product-header-row-vertical {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 18px;
}
.product-header-row-vertical .product-title {
  margin: 0;
  font-size: 1.5rem;
  min-width: 160px;
}
.product-header-row-vertical .product-meta {
  padding: 0 0 0 0;
  border: none;
  border-radius: 0;
  min-width: 120px;
  background: none;
}
.product-header-row-vertical .price {
  font-size: 1.3rem;
  margin: 0 0 2px 0;
}
.product-header-row-vertical .weight {
  font-size: 0.85rem;
  margin: 0;
}
.product-header-row-vertical .quantity-wrapper {
  min-width: 120px;
  margin-bottom: 0;
}
.product-header-row-vertical .qty-controls {
  margin-top: 0;
}

.product-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  line-height: 1.3;
}

.product-desc {
  font-size: 0.95rem;
  line-height: 1.7;
  color: #3d2060;
  word-break: break-word;
  overflow-wrap: break-word;
  white-space: pre-line;
  margin: 0;
}

.product-instructions {
  background: #f9f4ff;
  border-left: 4px solid #753BBD;
  border-radius: 4px;
  padding: 14px 16px;
}
.instructions-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #753BBD;
  margin: 0 0 6px 0;
}
.instructions-text {
  font-size: 0.9rem;
  line-height: 1.6;
  color: #444;
  word-break: break-word;
  white-space: pre-line;
  margin: 0;
}

.product-meta {
  padding: 16px 18px;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
}
.price {
  font-size: 1.8rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 4px 0;
}
.price span { color: #753BBD; }
.weight {
  font-size: 0.85rem;
  color: #888;
  margin: 0;
}

/* Buy actions */
.actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  border-top: 1px solid #f0f0f0;
  padding-top: 18px;
}

.quantity-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.quantity-wrapper label {
  font-size: 0.85rem;
  color: #777;
}
.qty-controls {
  display: flex;
  align-items: center;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: fit-content;
  overflow: hidden;
}
.qty-btn {
  background: #f5f5f5;
  border: none;
  width: 38px;
  height: 42px;
  font-size: 1.2rem;
  cursor: pointer;
  color: #555;
  transition: background 0.2s;
}
.qty-btn:hover { background: #e8e8e8; }
.quantity-input {
  width: 56px;
  height: 42px;
  padding: 0;
  font-size: 1rem;
  border: none;
  border-left: 1px solid #ddd;
  border-right: 1px solid #ddd;
  text-align: center;
  box-sizing: border-box;
  -moz-appearance: textfield;
}
.quantity-input::-webkit-outer-spin-button,
.quantity-input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }

.add-to-cart-button {
  background-color: #753BBD;
  color: white;
  padding: 14px 24px;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  width: 100%;
  letter-spacing: 0.3px;
}
.add-to-cart-button:hover { background-color: #5e2ea0; }

/* Cart */
.cart-wrapper {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  max-width: 350px;
}

/* Mobile */
@media (max-width: 768px) {
  .product-container { flex-direction: column; }
  .image-section, .info-section {
    flex: 0 0 100%;
    max-width: 100%;
  }
  .info-section { padding: 20px; }
  .cart-wrapper { top: 10px; right: 10px; max-width: 280px; }
}
@media (max-width: 900px) {
  .product-header-row-horizontal {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  .product-header-row-horizontal .product-title,
  .product-header-row-horizontal .product-meta,
  .product-header-row-horizontal .quantity-wrapper {
    min-width: 0;
    padding: 0;
  }
}
</style>
