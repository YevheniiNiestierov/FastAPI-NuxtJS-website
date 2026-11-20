<template>
  <div class="thank-you-wrapper">
    <div class="thank-you-card">
      <div class="success-icon">✓</div>
      <h1>Дякуємо за замовлення!</h1>
      <p class="message">
        Наш менеджер звʼяжеться з вами у найближчий час.
      </p>
      <div v-if="orderNumber" class="order-number-box">
        <span>Номер вашого замовлення:</span>
        <strong>№ {{ orderNumber }}</strong>
      </div>
      <NuxtLink to="/" class="home-button">
        Повернутися до магазину
      </NuxtLink>
    </div>
  </div>
</template>

<script setup>
usePageSeo({ title: 'Дякуємо за замовлення — Natur Savon', description: 'Ваше замовлення прийнято.', noindex: true });
import { computed } from 'vue';
import { useRoute } from '#app';

const route = useRoute();
const orderNumber = computed(() => route.query.order || '');
</script>

<style scoped>
.thank-you-wrapper {
  --primary-color: #753BBD;
  --primary-hover: #984ABD;
  --text-dark: #1e293b;
  --text-muted: #64748b;

  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.thank-you-card {
  background: white;
  width: 100%;
  max-width: 500px;
  padding: 48px 40px;
  border-radius: 20px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.success-icon {
  width: 64px;
  height: 64px;
  background-color: #dcfce7;
  color: #16a34a;
  font-size: 2rem;
  font-weight: bold;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
}

h1 {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--text-dark);
  margin: 0 0 12px 0;
}

.message {
  color: var(--text-muted);
  font-size: 1.05rem;
  line-height: 1.5;
  margin-bottom: 28px;
}

.order-number-box {
  background-color: #f8fafc;
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 32px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.order-number-box span {
  font-size: 0.9rem;
  color: var(--text-muted);
}

.order-number-box strong {
  font-size: 1.4rem;
  color: var(--primary-color);
  letter-spacing: 0.5px;
}

.home-button {
  display: inline-block;
  width: 100%;
  padding: 16px;
  background-color: var(--primary-color);
  color: white;
  text-decoration: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  transition: all 0.2s;
  box-shadow: 0 4px 6px -1px rgba(117, 59, 189, 0.2);
}

.home-button:hover {
  background-color: var(--primary-hover);
  transform: translateY(-1px);
}
</style>