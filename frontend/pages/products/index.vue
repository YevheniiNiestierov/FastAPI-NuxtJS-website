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
        src="/natur_savon_logo.png"
        alt="Brand Logo"
        class="brand-image"
      >
    </section>

    <main class="main-content">
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
          <div v-for="product in filteredProducts" :key="product.id" class="product-card">
            <div class="image-container">
              <NuxtLink :to="`/products/${product.id}`" class="image-link">
                <img :src="product.imageUrl" :alt="product.title" class="product-image product-image--base" />
                <img
                  v-if="product.imageKeys.length > 1"
                  :src="product.hoverImageUrl"
                  :alt="product.title"
                  class="product-image product-image--hover"
                />
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
              <NuxtLink :to="`/products/${product.id}`" class="details-link">Детальніше про товар</NuxtLink>
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRuntimeConfig, useState } from '#app';

const products = ref([]);
const productTypes = ref([]);
const selectedType = ref(null);
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

const filteredProducts = computed(() => {
  if (!selectedType.value) return products.value;
  return products.value.filter(p => p.product_type === selectedType.value);
});

const fetchTypes = async () => {
  try {
    const data = await $fetch(`${config.public.apiBase}/product/types/`);
    productTypes.value = data.types;
  } catch (error) {
    console.error('Error fetching types:', error);
  }
};

const fetchProducts = async () => {
  try {
    // GET /product/products now returns products with their gallery images embedded.
    // No per-product follow-up requests are needed — the N+1 problem is gone.
    const data = await $fetch(`${config.public.apiBase}/product/products`);
    products.value = data.map(product => {
      const images = product.images ?? [];   // ImageItem[]  { key, cdn_url }
      return {
        ...product,
        quantity: 1,
        imageUrl: images[0]?.cdn_url ?? '',
        hoverImageUrl: images[1]?.cdn_url ?? null,
        imageKeys: images.map(img => img.key),
      };
    });
  } catch (error) {
    console.error('Error fetching products:', error);
  }
};


const addItemToCart = async (product) => {
  try {
    await $fetch(`${config.public.apiBase}/cart/add/${product.id}`, {
      method: 'POST',
      headers: { 'Session-ID': sessionID.value },
      params: { quantity: product.quantity }
    });
    await fetchProductsAndTotalSum();
    alert(`Товар "${product.title}" додано до кошика!`);
  } catch (error) {
    console.error('Error adding product:', error);
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
  await fetchTypes();
  refreshIsAdmin();
});

onUnmounted(() => {});

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

/* Type filter bar */
.type-filter {
  max-width: 1200px;
  margin: 0 auto 28px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-btn {
  flex: 1 1 0;
  min-width: 80px;
  max-width: 200px;
  padding: 8px 12px;
  border: 2px solid #753BBD;
  border-radius: 24px;
  background: white;
  color: #753BBD;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  text-align: center;
  transition: background 0.18s, color 0.18s;
}

.filter-btn:hover,
.filter-btn.active {
  background: #753BBD;
  color: white;
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

.header-nav {
  display: flex;
  gap: 18px;
  align-items: center;
}

.nav-link {
  color: #753BBD;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  transition: color 0.2s;
}

.nav-link:hover {
  color: #984ABD;
  text-decoration: underline;
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
  position: relative;
}

.image-link {
  display: block;
  width: 100%;
  height: 100%;
  cursor: pointer;
  position: relative;
}

.product-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-image--base {
  opacity: 1;
}

.product-image--hover {
  opacity: 0;
}

.product-card:hover .product-image--base {
  opacity: 0;
}

.product-card:hover .product-image--hover {
  opacity: 1;
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
  -webkit-line-clamp: 2;
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

/* Quantity Controls */
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

