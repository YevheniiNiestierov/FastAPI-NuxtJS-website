<template>
  <div class="create-order-container">
    <h1>Create Order</h1>
    <form @submit.prevent="createOrder" class="order-form">
      <div class="form-group">
        <label for="delivery_type">Вид доставки:</label>
        <select id="delivery_type" v-model="order.delivery_type" required>
          <option v-for="(delivery_type, index) in delivery_types" :key="index" :value="delivery_type">
            {{ delivery_type }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="name">ПІБ:</label>
        <textarea id="name" v-model="order.name" required></textarea>
      </div>

      <div class="form-group">
        <label for="city">City:</label>
        <input type="text" id="city" v-model="order.city" required>
      </div>

      <div class="form-group">
        <label for="department_number">Номер відділення / Поштовий індекс:</label>
        <textarea id="department_number" v-model.lazy="order.department_number" required></textarea>
      </div>

      <div class="form-group">
        <label for="phone_number">Номер телефону:</label>
        <input type="text" id="phone_number" v-model.lazy="order.phone_number" required>
      </div>

      <button type="submit" class="submit-button">Create Order</button>
    </form>

    <div class="navigation-links">
      <NuxtLink to="/customer">Go back</NuxtLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useFetch, useRuntimeConfig } from '#app';

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
  if (!localStorage.getItem('sessionID')) {
    localStorage.setItem('sessionID', sessionID.value);
  }
}

const config = useRuntimeConfig();

const createOrder = async () => {
  try {
    await useFetch(`${config.public.apiBase}/order/create_order/`, {
      method: 'POST',
      headers: {
        'Session-ID': order.value.user_id,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(order.value)
    });
    alert('Ордер створено');
    console.log('Order created successfully!');
    // Optionally, you can redirect the user to another page after successful creation
    // navigateTo('/products');
  } catch (error) {
    console.error('Error creating order:', error);
  }
};

const getDeliveryTypes = async () => {
  const config = useRuntimeConfig();
  try {
    const { data } = await useFetch(`${config.public.apiBase}/order/delivery_types/`);
    delivery_types.value = data.value.delivery_types;
  } catch (error) {
    console.error('Error fetching delivery types:', error);
  }
};


onMounted(() => {
  getDeliveryTypes();
});
</script>

<style scoped>
.create-order-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  border-radius: 8px;
  background-color: #f9f9f9;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

h1 {
  text-align: center;
  margin-bottom: 20px;
}

.order-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input,
textarea,
select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.submit-button {
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  background-color: #42b983;
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-button:hover {
  background-color: #369b74;
}

.navigation-links {
  margin-top: 20px;
  text-align: center;
}
</style>
