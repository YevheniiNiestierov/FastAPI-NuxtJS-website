<script setup>
import { onMounted, computed, ref } from "vue";
import { useFetch, useRuntimeConfig, useState } from "#app";

const config = useRuntimeConfig();

// -- State --
const productsInCart = useState('productsInCart', () => []);
const totalPrice = useState('totalPrice', () => 0);
const sessionID = useState('sessionID', () => null);

const isCartExpanded = ref(true);

// -- Methods --
const toggleCart = () => {
  isCartExpanded.value = !isCartExpanded.value;
};

// Helper to generate image URL
const getImageUrl = (title) => {
  if (!title) return '';
  return `${config.public.apiBase}/image/images/${encodeURIComponent(title)}`;
};

const initSession = () => {
  if (process.client) {
    let stored = localStorage.getItem('sessionID');
    if (!stored) {
      stored = crypto.randomUUID();
      localStorage.setItem('sessionID', stored);
    }
    sessionID.value = stored;
  }
};

const fetchProductsAndTotalSum = async () => {
  if (!sessionID.value) return;

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

const removeItemFromCart = async (productId) => {
  try {
    await $fetch(`${config.public.apiBase}/cart/delete/${productId}`, {
      headers: { 'Session-ID': sessionID.value }
    });
    await fetchProductsAndTotalSum();
  } catch (error) {
    console.error('Error removing product:', error);
  }
};

const increaseQuantity = async (product) => {
  try {
    await $fetch(`${config.public.apiBase}/cart/add/${product.id}`, {
      method: 'POST',
      headers: { 'Session-ID': sessionID.value },
      params: { quantity: 1 }
    });
    await fetchProductsAndTotalSum();
  } catch (error) {
    console.error('Error increasing quantity:', error);
  }
};

// -- Computed --
const hasItems = computed(() => {
  if (Array.isArray(productsInCart.value)) {
    return productsInCart.value.length > 0;
  }
  return Object.keys(productsInCart.value).length > 0;
});

// -- Lifecycle --
onMounted(async () => {
  initSession();
  await fetchProductsAndTotalSum();
});
</script>

<template>
  <div class="cart-container">
    <div class="cart-header-wrapper" @click="toggleCart" title="Розгорнути / Згорнути">
      <h2 class="cart-header">Кошик</h2>
      <button class="toggle-button" :aria-expanded="isCartExpanded" aria-label="Toggle cart">
        <span class="toggle-text">{{ isCartExpanded ? 'Згорнути' : 'Розгорнути' }}</span>
        <span :class="['chevron', { 'chevron-up': isCartExpanded }]">▼</span>
      </button>
    </div>

    <div v-show="isCartExpanded" class="cart-body">
      <div v-if="hasItems" class="cart-content">
        <ul class="cart-list">
          <li v-for="(product, index) in productsInCart" :key="product.id || index" class="cart-item">

            <NuxtLink :to="`/products/${product.id}`" class="item-image">
               <img :src="getImageUrl(product.title)" :alt="product.title" />
            </NuxtLink>

            <div class="item-details">
              <h3 class="item-title">
                <NuxtLink :to="`/products/${product.id}`">{{ product.title }}</NuxtLink>
              </h3>
              <span class="item-quantity">Кількість: <strong>{{ product.quantity }}</strong></span>
            </div>

            <div class="button-group">
              <button
                @click="increaseQuantity(product)"
                class="increase-button"
                title="Збільшити кількість"
              >
                +
              </button>

              <button
                @click="removeItemFromCart(product.id)"
                class="remove-button"
                title="Видалити один"
              >
                −
              </button>
            </div>
          </li>
        </ul>

        <div class="cart-summary">
          <div class="total-row">
            <span>Загальна ціна:</span>
            <span class="total-price">{{ totalPrice }} грн.</span>
          </div>

          <NuxtLink to="/order" class="checkout-button">
            Створити замовлення
          </NuxtLink>
        </div>
      </div>

      <div v-else class="empty-cart-message">
        <p>Ваш кошик пустий</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cart-container {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 20px;
  max-width: 100%;
}

/* Header Styles for Wrap/Unwrap */
.cart-header-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  cursor: pointer;
  user-select: none;
  transition: opacity 0.2s ease;
}

.cart-header-wrapper:hover {
  opacity: 0.8;
}

.cart-header {
  font-size: 1.5rem;
  margin: 0;
  color: #333;
}

.toggle-button {
  background: none;
  border: none;
  font-size: 1rem;
  color: #753BBD;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px;
  gap: 8px; /* Adds space between text and chevron */
}

.toggle-text {
  font-weight: 500;
  font-weight: bold;
}

.chevron {
  display: inline-block;
  transition: transform 0.3s ease;
  font-size: 0.9rem;
}

.chevron-up {
  transform: rotate(180deg);
}

.cart-body {
  margin-top: 20px;
}

/* Existing List Styles */
.cart-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.cart-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
  gap: 15px;
}

.item-image {
  display: inline-block;
  text-decoration: none;
}

.item-image img {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #ddd;
  transition: opacity 0.2s;
}

.item-image:hover img {
  opacity: 0.8;
}

.item-details {
  flex-grow: 1;
}

.item-title {
  font-size: 1rem;
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.item-title a {
  color: inherit;
  text-decoration: none;
  transition: color 0.2s;
}

.item-title a:hover {
  color: #753BBD;
}

.item-quantity {
  font-size: 0.9rem;
  color: #666;
}

.button-group {
  display: flex;
  gap: 1px;
}

/* Buttons */
.increase-button {
  background-color: #753BBD;
  color: white;
  border: none;
  border-radius: 4px;
  width: 30px;
  height: 30px;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.increase-button:hover {
  background-color: #984ABD;
}

.remove-button {
  background-color: #753BBD;
  color: white;
  border: none;
  border-radius: 4px;
  width: 30px;
  height: 30px;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.remove-button:hover {
  background-color: #d32f2f;
}

/* Footer & Total */
.cart-summary {
  margin-top: 20px;
  text-align: right;
}

.total-row {
  font-size: 1.2rem;
  margin-bottom: 15px;
  color: #333;
}

.total-price {
  font-weight: bold;
  color: #4CAF50;
  margin-left: 10px;
}

.checkout-button {
  display: inline-block;
  background-color: #753BBD;
  color: white;
  padding: 12px 24px;
  text-decoration: none;
  border-radius: 4px;
  font-weight: bold;
  transition: background 0.3s;
  width: 100%;
  text-align: center;
}

.checkout-button:hover {
  background-color: #984ABD;
}

/* Empty State */
.empty-cart-message {
  text-align: center;
  color: #888;
  padding: 20px;
  font-style: italic;
}

@media (min-width: 768px) {
  .checkout-button {
    width: auto;
  }
}
</style>