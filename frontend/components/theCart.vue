<script setup>
import {onMounted, ref} from "vue";
import {useFetch, useRuntimeConfig} from "#app";

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

onMounted(async () => {
  if (process.client) {
    await fetchProductsAndTotalSum();
  }
});
</script>

<template>
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
</template>

<style scoped>

</style>