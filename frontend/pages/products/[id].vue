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
            v-for="imageObj in imageGallery"
            :key="imageObj.key"
            :src="getThumbnailUrl(imageObj)"
            :alt="`Thumbnail for ${product.title}`"
            @click="setActiveImage(imageObj)"
            :class="{ active: activeImage?.key === imageObj.key }"
            class="thumbnail-image"
          />
        </div>
      </div>

      <div class="info-section">
        <h1 class="product-title">{{ product.title }}</h1>
        <p class="product-desc">{{ product.description }}</p>

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
      <NuxtLink to="/" class="back-link">
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
import { useFetch, useRoute, useRuntimeConfig, useState } from "#app";

// Config & Route
const config = useRuntimeConfig();
const route = useRoute();
const productId = route.params.id;

// State
const product = ref(null);
const selectedQuantity = ref(1); // Local state for input
const sessionID = ref(null);
const pending = ref(true); // Loading state
const imageGallery = ref([]);
const activeImage = ref(null);

// Global State (Shared with Cart)
const productsInCart = useState('productsInCart', () => []);
const totalPrice = useState('totalPrice', () => 0);

// The CDN serves original files for both main image and thumbnails
const mainImageUrl = computed(() => activeImage.value?.cdn_url || '');

const getThumbnailUrl = (imageObj) => imageObj?.cdn_url || '';

const setActiveImage = (imageObj) => {
  activeImage.value = imageObj;
};

const fallbackImage = (title) => ({
  key: `${title}_1`,
  cdn_url: `${config.public.cdnBase}/${encodeURIComponent(`${title}_1.webp`)}`
});

// -- API Methods --

const fetchProduct = async () => {
  pending.value = true;
  try {
    const data = await $fetch(`${config.public.apiBase}/product/products/${productId}`);
    product.value = data;
    // Canonical URL: old UUID links and stale slugs resolve, then redirect to the current slug
    if (data.slug && data.slug !== productId) {
      await navigateTo(`/products/${data.slug}`, { replace: true, redirectCode: 301 });
      return;
    }
    await fetchImageGallery(); // Fetch gallery after product is loaded
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
      activeImage.value = data[0]; // Set the first image as active
    } else {
      // Fallback: default <title>_1.webp on the CDN
      const fb = fallbackImage(product.value.title);
      imageGallery.value = [fb];
      activeImage.value = fb;
    }
  } catch (error) {
    console.error('Error fetching image gallery:', error);
    const fb = fallbackImage(product.value.title);
    imageGallery.value = [fb];
    activeImage.value = fb;
  }
};

const addItemToCart = async () => {
  if (!sessionID.value) return;

  try {
    // Use product_id instead of id
    const productId = product.value.product_id || product.value.id;

    await $fetch(`${config.public.apiBase}/cart/add/${productId}`, {
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
      // Handle both response formats
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



// -- Lifecycle --

onMounted(async () => {
  if (process.client) {
    // Session Management
    let storedSession = localStorage.getItem('sessionID');
    if (!storedSession) {
      storedSession = crypto.randomUUID();
      localStorage.setItem('sessionID', storedSession);
    }
    sessionID.value = storedSession;

    // Initial Data Load
    await fetchProduct();
    await fetchProductsAndTotalSum();
  }
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
