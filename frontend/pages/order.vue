<template>
  <div class="checkout-wrapper">
    <div class="checkout-card">
      <header class="checkout-header">
        <NuxtLink to="/customer" class="back-link">
          <span class="arrow">←</span> Назад до магазину
        </NuxtLink>
        <h1>Оформлення замовлення</h1>
        <p class="subtitle">Будь ласка, заповніть дані для доставки</p>
      </header>

      <form @submit.prevent="createOrder" class="order-form">
        <div class="form-group">
          <label for="delivery_type">Спосіб доставки</label>
          <select id="delivery_type" v-model="order.delivery_type" required class="form-control">
            <option value="" disabled selected>Оберіть варіант...</option>
            <option v-for="(type, index) in delivery_types" :key="index" :value="type">
              {{ type }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="name">ПІБ Отримувача</label>
          <input
            type="text"
            id="name"
            v-model="order.name"
            placeholder="Іванов Іван Іванович"
            required
            class="form-control"
          >
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="city">Місто</label>
            <input
              type="text"
              id="city"
              v-model="order.city"
              placeholder="Київ"
              required
              class="form-control"
            >
          </div>

          <div class="form-group">
            <label for="department_number">Відділення / Індекс</label>
            <input
              type="text"
              id="department_number"
              v-model.lazy="order.department_number"
              placeholder="№12 або 01001"
              required
              class="form-control"
            >
          </div>
        </div>

        <div class="form-group">
          <label for="phone_number">Номер телефону</label>
          <input
            type="tel"
            id="phone_number"
            v-model.lazy="order.phone_number"
            placeholder="+380..."
            required
            class="form-control"
          >
        </div>

        <div class="form-actions">
          <button type="submit" class="submit-button">
            Підтвердити замовлення
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useFetch, useRuntimeConfig } from '#app';

const config = useRuntimeConfig();
const sessionID = ref(null);

const order = ref({
  name: '',
  delivery_type: '',
  city: '',
  department_number: '',
  phone_number: '',
  products: '',
  total_sum: null,
  user_id: ''
});

const delivery_types = ref([]);

if (process.client) {
  sessionID.value = localStorage.getItem('sessionID') || crypto.randomUUID();
  order.value.user_id = sessionID.value; // Assigning sessionID to user_id
}

const createOrder = async () => {
  try {
    await useFetch(`${config.public.apiBase}/order/create_order/`, {
      method: 'POST',
      headers: {
        'Session-ID': sessionID.value,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(order.value)
    });
    alert('✅ Замовлення успішно створено!');
  } catch (error) {
    console.error('Error creating order:', error);
    alert('Помилка при створенні замовлення');
  }
};

const getDeliveryTypes = async () => {
  try {
    const { data } = await useFetch(`${config.public.apiBase}/order/delivery_types/`);
    if (data.value) delivery_types.value = data.value.delivery_types;
  } catch (error) {
    console.error('Error fetching delivery types:', error);
  }
};

onMounted(() => {
  getDeliveryTypes();
});
</script>

<style scoped>
/* Scoped variables for easy changes */
.checkout-wrapper {
  --primary-color: #2563eb;
  --primary-hover: #1d4ed8;
  --bg-color: #f1f5f9;
  --text-dark: #1e293b;
  --text-muted: #64748b;

  min-height: 100vh;
  background-color: var(--bg-color);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.checkout-card {
  background: white;
  width: 100%;
  max-width: 550px;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
}

.checkout-header {
  margin-bottom: 32px;
  text-align: center;
}

.back-link {
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  transition: color 0.2s;
}

.back-link:hover {
  color: var(--primary-color);
}

.checkout-header h1 {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--text-dark);
  margin: 0 0 8px 0;
}

.subtitle {
  color: var(--text-muted);
  font-size: 0.95rem;
}

/* Form Styling */
.order-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

@media (max-width: 480px) {
  .form-row { grid-template-columns: 1fr; }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-dark);
  margin-left: 2px;
}

.form-control {
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.2s;
  background-color: #fafafa;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary-color);
  background-color: white;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
}

.form-control::placeholder {
  color: #cbd5e1;
}

/* Button Styling */
.form-actions {
  margin-top: 10px;
}

.submit-button {
  width: 100%;
  padding: 16px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
}

.submit-button:hover {
  background-color: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
}

.submit-button:active {
  transform: translateY(0);
}
</style>