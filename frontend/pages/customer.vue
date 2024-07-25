<template>
  <div class="products-container">
    <h1>Асортимент</h1>
    <ul class="product-list">
      <li v-for="product in products" :key="product.id" class="product-item">
        <h2>{{ product.title }}</h2>
        <img :src="product.imageUrl" alt="Product Image" class="product-image">
        <p>{{ product.description }}</p>
        <p>Ціна:{{ product.price }} грн.</p>
        <p>Вага: {{ product.weight }} г.</p>
        <div class="product-actions">
          <input type="number" v-model.number="product.quantity" min="1" class="quantity-input" />
          <button @click="addItemToCart(product)" class="add-to-cart-button">Додати до кошика</button>
            <a :href="`/products/${product.product_id}`">Детальніше</a>
        </div>
      </li>
    </ul>
    <div class="cart-section">
      <h2>Кошик</h2>
      <ul v-if="Object.keys(productsInCart).length > 0" class="cart-list">
        <li v-for="(product, id) in productsInCart" :key="id" class="cart-item">
          {{ product.title }} - кількість: {{ product.quantity }}
          <div class="cart-actions">
            <button @click="removeItemFromCart(product.id)" class="remove-button">Видалити 1</button>
          </div>
        </li>
        Загальна ціна: {{totalPrice}} грн.
        <NuxtLink class="create-order-button" to="/order">Створити замовлення</NuxtLink>
      </ul>
      <div v-else class="empty-cart-message">
        Ваш кошик пустий
      </div>
    </div>

    <div class="navigation-links">
      <NuxtLink to="/manager">Менеджерська сторінка</NuxtLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useFetch, useRuntimeConfig } from '#app';

const products = ref([]);
const totalPrice = ref();
const productsInCart = ref({});
const sessionID = ref(null);


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
      imageUrl: `${config.public.apiBase}/image/images/${product.title}`
    }));
    console.log(products.value, 'list of products')
  } catch (error) {
    console.error('Error fetching products:', error);
  }
};

const addItemToCart = async (product) => {
  try {
    await useFetch(`${config.public.apiBase}/cart/add/${product.product_id}`, {
      headers: { 'Session-ID': sessionID.value },
      params: { quantity: product.quantity }
    });
    await fetchProductsAndTotalSum();
    alert('Product added to basket');
  } catch (error) {
    console.error('Error adding product to basket:', error);
  }
};

const removeItemFromCart = async (productId) => {
  try {
    await useFetch(`${config.public.apiBase}/cart/delete/${productId}`, {
      headers: { 'Session-ID': sessionID.value }
    });
    await fetchProductsAndTotalSum();
  } catch (error) {
    console.error('Error removing product:', error);
  }
};

const fetchProductsAndTotalSum = async () => {
  try {
    const { data } = await useFetch(`${config.public.apiBase}/cart/cart-products-and_total-price`, {
      headers: { 'Session-ID': sessionID.value }
    });
    productsInCart.value = data.value[0];
    totalPrice.value = data.value[1]
  } catch (error) {
    console.error('Error fetching products in cart:', error);
  }
};


onMounted(async () => {
  if (process.client) {
    await fetchProducts();
    await fetchProductsAndTotalSum();
  }
});
</script>

<style scoped>
.products-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

h1, h2 {
  text-align: center;
  margin-bottom: 20px;
}

.product-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.product-item {
  flex: 1 1 calc(33.333% - 20px);
  box-sizing: border-box;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #fff;
}

.product-image {
  max-width: 100%;
  height: auto;
  display: block;
  margin-bottom: 10px;
}

.product-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quantity-input {
  width: 60px;
}

.add-to-cart-button, .remove-button, .create-order-button{
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  background-color: #42b983;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}


.add-to-cart-button:hover, .remove-button:hover {
  background-color: #369b74;
}

.cart-section {
  margin-top: 30px;
}

.empty-cart-message {
  text-align: center;
  font-style: italic;
  color: #999;
}

.navigation-links {
  text-align: center;
  margin-top: 30px;
}

.navigation-links a {
  margin: 0 10px;
  color: #42b983;
  text-decoration: none;
}
</style>
