<template>
  <div class="page-wrapper">
    <div v-if="pending && !product" class="loading">
      Завантаження...
    </div>

    <div v-else-if="product" class="product-container">
      <div class="image-section">
        <img :src="mainImageUrl" :alt="product.title" class="product-image" />
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
      </div>

      <div class="info-section">
        <h1 class="product-title">{{ product.title }}</h1>
        <p class="product-desc">{{ product.description }}</p>

        <div v-if="product.instructions" class="product-instructions">
          <h3 class="instructions-title">Інструкція із застосування</h3>
          <p class="instructions-text">{{ product.instructions }}</p>
        </div>

        <div class="product-meta">
          <p class="price">Ціна: <span>{{ product.price }} грн.</span></p>
          <p class="weight">Вага: {{ product.weight }} г.</p>
        </div>

        <div class="actions">
          <div class="quantity-wrapper">
            <label for="qty">Кількість:</label>
            <input
              id="qty"
              type="number"
              v-model.number="selectedQuantity"
              min="1"
              class="quantity-input"
            />
          </div>

          <button @click="addItemToCart" class="add-to-cart-button">
            Додати до кошика
          </button>
        </div>
      </div>
      <NuxtLink to="/customer" class="back-link">
        <span class="arrow">←</span> Назад до магазину
      </NuxtLink>
    </div>

    <div class="cart-wrapper">
      <theCart />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from "vue";
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

// Computed Image URL
const mainImageUrl = computed(() => {
  if (!activeImageKey.value) return '';
  const encodedKey = encodeURIComponent(activeImageKey.value);
  return `${config.public.apiBase}/image/images/${encodedKey}?width=1920&quality=95`;
});

const getThumbnailUrl = (key) => {
  if (!key) return '';
  return `${config.public.apiBase}/image/images/${encodeURIComponent(key)}?width=200&quality=80`;
};

const setActiveImage = (key) => {
  activeImageKey.value = key;
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
    const data = await $fetch(`${config.public.apiBase}/image/images/gallery/${encodedTitle}`);
    if (data && data.length > 0) {
      imageGallery.value = data;
      activeImageKey.value = data[0];
    } else {
      imageGallery.value = [product.value.title];
      activeImageKey.value = product.value.title;
    }
  } catch {
    imageGallery.value = [product.value.title];
    activeImageKey.value = product.value.title;
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

  // route.params.id can be undefined during client-side navigation (Nuxt SSR hydration timing).
  // Fall back to parsing the UUID directly from the URL, which is always correct.
  const id = route.params.id || window.location.pathname.split('/').filter(Boolean).pop();
  if (id) {
    await fetchProduct(id);
  }
  await fetchProductsAndTotalSum();
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

/* Flex Container for 2-Column Layout */
.product-container {
  display: flex;
  gap: 40px;
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  align-items: flex-start;
}

/* Left Column */
.image-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  min-height: 400px;
}

.product-image {
  max-width: 100%;
  max-height: 500px;
  object-fit: contain;
  border-radius: 8px;
}

.thumbnail-gallery {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}

.thumbnail-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.3s;
}

.thumbnail-image:hover {
  border-color: #ccc;
}

.thumbnail-image.active {
  border-color: #753BBD;
}


/* Right Column */
.info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.product-title {
  font-size: 2rem;
  margin-bottom: 10px;
  color: #333;
}

.product-desc {
  font-size: 1rem;
  line-height: 1.6;
  color: #555;
  word-break: break-word;
  overflow-wrap: break-word;
  white-space: pre-line;
}

.product-instructions {
  background: #f9f4ff;
  border-left: 4px solid #753BBD;
  border-radius: 4px;
  padding: 14px 16px;
}

.instructions-title {
  font-size: 1rem;
  font-weight: 700;
  color: #753BBD;
  margin: 0 0 8px 0;
}

.instructions-text {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #444;
  word-break: break-word;
  overflow-wrap: break-word;
  white-space: pre-line;
  margin: 0;
}

.product-meta {
  background: #f4f4f4;
  padding: 15px;
  border-radius: 6px;
  width: fit-content;
  height: fit-content;
}

.price {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.weight {
  font-size: 0.9rem;
  color: #777;
}

.actions {
  display: flex;
  align-items: flex-end; /* Align items to the bottom */
  gap: 15px;
  margin-top: 20px;
  flex-wrap: wrap; /* Allow wrapping on smaller screens */
}

.quantity-wrapper {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.quantity-wrapper label {
  font-size: 0.9rem;
  color: #555;
}

.quantity-input {
  width: 80px;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  text-align: center;
  height: 48px; /* Match button height */
  box-sizing: border-box;
}

.cart-wrapper {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  max-width: 350px;
}

@media (max-width: 768px) {
  .cart-wrapper {
    top: 10px;
    right: 10px;
    max-width: 280px;
  }
}

.add-to-cart-button {
  background-color: #753BBD;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
  flex-grow: 1;
  height: 48px; /* Explicit height */
  box-sizing: border-box;
}

.add-to-cart-button:hover {
  background-color: #984ABD;
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .product-container {
    flex-direction: column;
  }

  .actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
