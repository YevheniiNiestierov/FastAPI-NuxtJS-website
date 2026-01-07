<script setup>
import { onMounted, computed } from "vue";
import { useFetch, useRuntimeConfig, useState } from "#app";

const config = useRuntimeConfig();

// -- State --
// We use useState ('key') to share data between this component and the Product Page
const productsInCart = useState('productsInCart', () => []);
const totalPrice = useState('totalPrice', () => 0);
const sessionID = useState('sessionID', () => null);

// -- Methods --

// Helper to generate image URL (same as Product Page)
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


const removeItemFromCart = async (productId) => {
  try {
    await useFetch(`${config.public.apiBase}/cart/delete/${productId}`, {
      headers: { 'Session-ID': sessionID.value }
    });
    // Refresh the list after deletion
    await fetchProductsAndTotalSum();
  } catch (error) {
    console.error('Error removing product:', error);
  }
};

// -- Computed --
const hasItems = computed(() => {
  // Handle case where productsInCart might be an object or array
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
    <h2 class="cart-header">Кошик</h2>

    <div v-if="hasItems" class="cart-content">
      <ul class="cart-list">
        <li v-for="(product, index) in productsInCart" :key="product.id || index" class="cart-item">

          <div class="item-image">
             <img :src="getImageUrl(product.title)" :alt="product.title" />
          </div>

          <div class="item-details">
            <h3 class="item-title">{{ product.title }}</h3>
            <span class="item-quantity">Кількість: <strong>{{ product.quantity }}</strong></span>
          </div>

          <button
            @click="removeItemFromCart(product.id)"
            class="remove-button"
            title="Видалити один"
          >
            &times;
          </button>
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
</template>

<style scoped>
/* Container matches the card style of the Product Page */
.cart-container {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 20px;
  margin-top: 30px; /* Space from content above */
  max-width: 100%;
}

.cart-header {
  font-size: 1.5rem;
  margin-bottom: 20px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

/* List Styles */
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

.item-image img {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.item-details {
  flex-grow: 1;
}

.item-title {
  font-size: 1rem;
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.item-quantity {
  font-size: 0.9rem;
  color: #666;
}

/* Buttons */
.remove-button {
  background-color: #ff5252; /* Red for destructive action */
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
  background-color: #4CAF50; /* Matches Product Page Add button */
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
  background-color: #45a049;
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