<template>
  <div class="page-wrapper">
    <div v-if="pending && !product" class="loading">
      Завантаження...
    </div>

    <div v-else-if="product" class="product-container">

      <div class="image-section">
        <img :src="imageUrl" :alt="product.title" class="product-image" />
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
        <NuxtLink to="/customer" class="back-link">
          <span class="arrow">←</span> Назад до магазину
        </NuxtLink>
    </div>

    <theCart />
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

// Global State (Shared with Cart)
const productsInCart = useState('productsInCart', () => []);
const totalPrice = useState('totalPrice', () => 0);

// Computed Image URL (Handles spaces/special chars in titles)
const imageUrl = computed(() => {
  if (!product.value?.title) return ''; // Add a placeholder image URL here if needed
  return `${config.public.apiBase}/image/images/${encodeURIComponent(product.value.title)}`;
});

// -- API Methods --

const fetchProduct = async () => {
  pending.value = true;
  try {
    const { data, error } = await useFetch(`${config.public.apiBase}/product/products/${productId}`);
    if (error.value) throw error.value;
    product.value = data.value;
  } catch (error) {
    console.error('Error fetching product:', error);
  } finally {
    pending.value = false;
  }
};

const addItemToCart = async () => {
  if (!sessionID.value) return;

  try {
    // Use product_id instead of id
    const productId = product.value.product_id || product.value.id;

    await useFetch(`${config.public.apiBase}/cart/add/${productId}`, {
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
    const { data } = await useFetch(`${config.public.apiBase}/cart/cart-products-and_total-price`, {
      headers: { 'Session-ID': sessionID.value }
    });
    if (data.value) {
      // Handle both response formats
      if (Array.isArray(data.value)) {
        productsInCart.value = data.value[0] || [];
        totalPrice.value = data.value[1] || 0;
      } else {
        productsInCart.value = data.value.products || [];
        totalPrice.value = data.value.total_sum || 0;
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
  justify-content: center;
  background: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
}

.product-image {
  max-width: 100%;
  max-height: 500px;
  object-fit: contain;
  border-radius: 4px;
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
  align-items: center;
  gap: 20px;
  margin-top: 20px;
}

.quantity-wrapper {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.quantity-input {
  width: 80px;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.add-to-cart-button {
  background-color: #4CAF50; /* Green */
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
  flex-grow: 1;
  max-width: 300px;
}

.add-to-cart-button:hover {
  background-color: #45a049;
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