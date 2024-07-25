<template>
  <div class="product-container">
    <h1>{{ product.title }}</h1>
    <p>Опис: {{ product.description }} </p>
    <p>Ціна: {{ product.price }} грн.</p>
    <p>Вага: {{ product.weight }} г.</p>
    <input type="number" v-model.number="product.quantity" min="1" class="quantity-input" />
    <button @click="addItemToCart(product)" class="add-to-cart-button">Додати до кошика</button>
    <img :src="imageUrl" alt="Product Image" class="product-image">
    <theCart />
  </div>
</template>

<script setup>

import { useFetch, useRoute, useRuntimeConfig } from "#app";
import {onMounted, ref} from "vue";


const route = useRoute();
const productId = useState(() => route.params.id);
const product = useState(() => ({}));
const config = useRuntimeConfig();
const imageUrl = ref()
const sessionID = ref(null);



if (process.client) {
  sessionID.value = localStorage.getItem('sessionID') || crypto.randomUUID();
  if (!localStorage.getItem('sessionID')) {
    localStorage.setItem('sessionID', sessionID.value);
  }
}

const fetchProduct = async () => {
  try {
    const { data } = await useFetch(`${config.public.apiBase}/product/products/${productId.value}`);
    product.value = data;
    imageUrl.value = `${config.public.apiBase}/image/images/${product.value.title}`
  } catch (error) {
    console.error('Error fetching product:', error);
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
    await fetchProduct();
    await fetchProductsAndTotalSum()
  }
});
</script>
