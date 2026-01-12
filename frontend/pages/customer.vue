<template>
  <div class="store-wrapper">
    <header class="store-header">
      <h1>Асортимент</h1>
      <NuxtLink v-if="isAdmin" to="/manager" class="admin-link">Панель менеджера</NuxtLink>
    </header>
    <section class="brand-section">
      <img
        src="/natur_savon_logo.png"
        alt="Brand Logo"
        class="brand-image"
      >
    </section>

    <main class="main-content">
      <section class="products-section">
        <div class="product-grid">
          <div v-for="product in products" :key="product.id" class="product-card">
            <div class="image-container">
              <NuxtLink :to="`/products/${product.id}`" class="image-link">
                <img :src="product.imageUrl" :alt="product.title" class="product-image" >
              </NuxtLink>
            </div>

            <div class="product-info">
              <h2 class="product-title">{{ product.title }}</h2>
              <p class="product-description">{{ product.description }}</p>

              <div class="product-meta">
                <span class="product-weight">{{ product.weight }} г.</span>
                <span class="product-price">{{ product.price }} ₴</span>
              </div>

              <div class="product-actions">
                <div class="quantity-controls">
                  <input type="number" v-model.number="product.quantity" min="1" class="qty-input" />
                </div>
                <button @click="addItemToCart(product)" class="btn-primary">
                  Додати
                </button>
              </div>
              <a :href="`/products/${product.id}`" class="details-link">Детальніше про товар</a>
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

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useFetch, useRuntimeConfig, useState } from '#app';

const products = ref([]);
const sessionID = ref(null);
const isAdmin = ref(false);

// Use shared state for cart
const productsInCart = useState('productsInCart', () => []);
const totalPrice = useState('totalPrice', () => 0);

if (process.client) {
  sessionID.value = localStorage.getItem('sessionID') || crypto.randomUUID();
  if (!localStorage.getItem('sessionID')) {
    localStorage.setItem('sessionID', sessionID.value);
  }
}

const config = useRuntimeConfig();

const fetchProducts = async () => {
  try {
    const { data } = await useFetch(`${config.public.apiBase}/product/products`);
    products.value = data.value.map(product => ({
      ...product,
      quantity: 1,
      imageUrl: `${config.public.apiBase}/image/images/${encodeURIComponent(product.title)}?width=800&quality=90`
    }));
  } catch (error) {
    console.error('Error fetching products:', error);
  }
};

const addItemToCart = async (product) => {
  try {
    await useFetch(`${config.public.apiBase}/cart/add/${product.id}`, {
      headers: { 'Session-ID': sessionID.value },
      params: { quantity: product.quantity }
    });
    await fetchProductsAndTotalSum();
  } catch (error) {
    console.error('Error adding product:', error);
  }
};

const fetchProductsAndTotalSum = async () => {
  if (!sessionID.value) return;
  try {
    const { data } = await useFetch(`${config.public.apiBase}/cart/cart-products-and_total-price`, {
      headers: { 'Session-ID': sessionID.value }
    });
    if (data.value) {
      // Handle both potential response formats to stay consistent
      if (Array.isArray(data.value)) {
        productsInCart.value = data.value[0] || [];
        totalPrice.value = data.value[1] || 0;
      } else {
        productsInCart.value = data.value.products || [];
        totalPrice.value = data.value.total_sum || 0;
      }
    }
  } catch (error) {
    console.error('Error fetching cart:', error);
  }
};

const refreshIsAdmin = () => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      isAdmin.value = false;
      return;
    }
    const payload = JSON.parse(atob(token.split('.')[1]));
    isAdmin.value = !!payload.is_admin;
  } catch {
    isAdmin.value = false;
  }
};

onMounted(async () => {
  await fetchProducts();
  await fetchProductsAndTotalSum();
  refreshIsAdmin();
});

// React if token changes elsewhere
watch(
  () => localStorage.getItem('access_token'),
  () => refreshIsAdmin()
);
</script>

<style scoped>
/* Modern Color Palette */
:root {
  --primary: #2563eb;
  --primary-hover: #1d4ed8;
  --bg-body: #f8fafc;
  --text-main: #1e293b;
  --text-muted: #64748b;
  --card-bg: #ffffff;
}

.store-wrapper {
  font-family: 'Inter', -apple-system, sans-serif;
  background-color: #f8fafc;
  min-height: 100vh;
  padding: 40px 20px;
  color: #1e293b;
}

.store-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto 40px;
}

.store-header h1 {
  font-size: 2rem;
  font-weight: 800;
  margin: 0;
}

.admin-link {
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
}

/* Layout Grid */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
}

/* Product Cards */
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.product-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.image-container {
  width: 100%;
  height: 200px;
  background: #f1f5f9;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-link {
  display: block;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.product-info {
  padding: 20px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.product-title {
  font-size: 1.25rem;
  margin: 0 0 8px;
  font-weight: 700;
}

.product-description {
  color: #64748b;
  font-size: 0.9rem;
  margin-bottom: 20px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2; /* Show only 2 lines */
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  margin-bottom: 15px;
}

.product-price {
  font-weight: 800;
  font-size: 1.2rem;
  color: #0f172a;
}

.product-weight {
  font-size: 0.85rem;
  color: #94a3b8;
}

/* Actions */
.product-actions {
  display: flex;
  gap: 10px;
}

.qty-input {
  width: 60px;
  padding: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  text-align: center;
}

.btn-primary {
  flex-grow: 1;
  background: #753BBD;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover { background: #984ABD; }

.details-link {
  display: block;
  text-align: center;
  margin-top: 15px;
  font-size: 0.8rem;
  color: #94a3b8;
  text-decoration: none;
}

/* Cart Styles */
.cart-wrapper {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  max-width: 350px;
  width: 100%;
}

@media (max-width: 768px) {
  .cart-wrapper {
    position: static;
    max-width: none;
    margin-top: 40px;
  }
}

.brand-section {
  max-width: 1120px;
  margin: 0 auto 40px;
  text-align: center;
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.brand-image {
  max-width: 300px;
  height: auto;
  object-fit: contain;
}

@media (max-width: 768px) {
  .brand-image {
    max-width: 200px;
  }
  .brand-section {
    padding: 20px;
  }
}

</style>
