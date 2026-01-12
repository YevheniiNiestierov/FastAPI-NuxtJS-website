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

      <!-- Cart Items Preview with Edit Controls -->
      <div v-if="!showPreview && cartItems.length > 0" class="cart-preview">
        <h3>Товари у кошику</h3>
        <div v-for="product in cartItems" :key="product.id" class="product-item-edit">
          <div class="product-info">
            <span class="product-name">{{ product.title }}</span>
            <span class="product-price">{{ product.price }} грн/шт</span>
          </div>
          <div class="product-controls">
            <button
              type="button"
              @click="decreaseQuantity(product.id)"
              class="quantity-btn"
              :disabled="product.quantity <= 1"
            >
              −
            </button>
            <span class="quantity">{{ product.quantity }}</span>
            <button
              type="button"
              @click="increaseQuantity(product.id)"
              class="quantity-btn"
            >
              +
            </button>
            <button
              type="button"
              @click="removeProduct(product.id)"
              class="delete-btn"
              title="Видалити товар"
            >
              ✕
            </button>
          </div>
          <span class="product-total">{{ product.price * product.quantity }} грн</span>
        </div>

        <div class="total-sum">
          <strong>Загальна сума: {{ cartTotal }} грн</strong>
        </div>
      </div>

      <!-- Order Form -->
      <form v-if="!showPreview" @submit.prevent="previewOrder" class="order-form">
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
          <button type="submit" class="submit-button" :disabled="cartItems.length === 0">
            Переглянути замовлення
          </button>
        </div>
      </form>

      <!-- Order Preview -->
      <div v-else class="order-preview">
        <h2>Перегляд замовлення</h2>

        <div class="preview-section">
          <h3>Дані отримувача</h3>
          <p><strong>ПІБ:</strong> {{ orderPreview.name }}</p>
          <p><strong>Телефон:</strong> {{ orderPreview.phone_number }}</p>
        </div>

        <div class="preview-section">
          <h3>Доставка</h3>
          <p><strong>Спосіб:</strong> {{ orderPreview.delivery_type }}</p>
          <p><strong>Місто:</strong> {{ orderPreview.city }}</p>
          <p><strong>Відділення:</strong> {{ orderPreview.department_number }}</p>
        </div>

        <div class="preview-section">
          <h3>Товари</h3>
            <div v-for="product in orderPreview.products" :key="product.id" class="product-item">
              <span>{{ product.title }} × {{ product.quantity }}</span>
              <span>{{ product.price * product.quantity }} грн</span>
            </div>
          <div class="total-sum">
            <strong>Загальна сума: {{ orderPreview.total_sum }} грн</strong>
          </div>
        </div>

        <div class="form-actions preview-actions">
          <button @click="showPreview = false" class="secondary-button">
            Редагувати
          </button>
          <button @click="confirmOrder" class="submit-button">
            Підтвердити замовлення
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useFetch, useRuntimeConfig } from '#app';

const config = useRuntimeConfig();
const sessionID = ref(null);
const showPreview = ref(false);
const orderPreview = ref(null);
const cartItems = ref([]);
const cartTotal = ref(0);

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
  order.value.user_id = sessionID.value;
}

const getCartItems = async () => {
  try {
    const { data } = await useFetch(`${config.public.apiBase}/cart/cart-products-and_total-price`, {
      headers: {
        'Session-ID': sessionID.value
      }
    });

    if (data.value) {
      cartItems.value = data.value.products || [];
      cartTotal.value = data.value.total_sum || 0;
    }
  } catch (error) {
    console.error('Error fetching cart:', error);
  }
};

const increaseQuantity = async (productId) => {
  try {
    await useFetch(`${config.public.apiBase}/cart/add/${productId}`, {
      headers: {
        'Session-ID': sessionID.value
      }
    });
    await getCartItems();
  } catch (error) {
    console.error('Error increasing quantity:', error);
  }
};

const decreaseQuantity = async (productId) => {
  try {
    await useFetch(`${config.public.apiBase}/cart/delete/${productId}`, {
      headers: {
        'Session-ID': sessionID.value
      }
    });
    await getCartItems();
  } catch (error) {
    console.error('Error decreasing quantity:', error);
  }
};

const removeProduct = async (productId) => {
  try {
    // You need to add this endpoint to your router
    await useFetch(`${config.public.apiBase}/cart/delete/${productId}`, {
      headers: {
        'Session-ID': sessionID.value
      }
    });
    await getCartItems();
  } catch (error) {
    console.error('Error removing product:', error);
  }
};


const previewOrder = async () => {
  if (cartItems.value.length === 0) {
    alert('Кошик порожній');
    return;
  }

  try {
    const { data, error } = await useFetch(`${config.public.apiBase}/order/preview_order/`, {
      method: 'POST',
      headers: {
        'Session-ID': sessionID.value,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(order.value)
    });

    if (error.value) {
      alert('Помилка при перегляді замовлення');
      return;
    }

    orderPreview.value = data.value;
    showPreview.value = true;
  } catch (error) {
    console.error('Error previewing order:', error);
    alert('Помилка при перегляді замовлення');
  }
};

const confirmOrder = async () => {
  try {
    const { error } = await useFetch(`${config.public.apiBase}/order/create_order/`, {
      method: 'POST',
      headers: {
        'Session-ID': sessionID.value,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(order.value)
    });

    if (error.value) {
      alert('Помилка при створенні замовлення');
      return;
    }

    alert('✅ Замовлення успішно створено!');
    showPreview.value = false;
    order.value = {
      name: '',
      delivery_type: '',
      city: '',
      department_number: '',
      phone_number: '',
      products: '',
      total_sum: null,
      user_id: sessionID.value
    };
    cartItems.value = [];
    cartTotal.value = 0;
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
  getCartItems();
});
</script>

<style scoped>
.checkout-wrapper {
  --primary-color: #753BBD;
  --primary-hover: #984ABD;
  --bg-color: #f1f5f9;
  --text-dark: #1e293b;
  --text-muted: #64748b;
  --danger-color: #dc2626;

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

.cart-preview {
  padding: 20px;
  background-color: #f8fafc;
  border-radius: 12px;
  margin-bottom: 24px;
}

.cart-preview h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-dark);
  margin: 0 0 16px 0;
}

.product-item-edit {
  display: grid;
  grid-template-columns: 1fr auto auto;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #e2e8f0;
}

.product-item-edit:last-child {
  border-bottom: none;
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.product-name {
  font-weight: 500;
  color: var(--text-dark);
}

.product-price {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.product-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quantity-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #e2e8f0;
  background-color: white;
  border-radius: 6px;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quantity-btn:hover:not(:disabled) {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.quantity-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.quantity {
  min-width: 30px;
  text-align: center;
  font-weight: 600;
  color: var(--text-dark);
}

.delete-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #fee2e2;
  background-color: #fef2f2;
  color: var(--danger-color);
  border-radius: 6px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-btn:hover {
  background-color: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.product-total {
  font-weight: 600;
  color: var(--text-dark);
  white-space: nowrap;
}

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
  .product-item-edit {
    grid-template-columns: 1fr;
  }
  .product-controls {
    justify-content: space-between;
  }
  .product-total {
    text-align: right;
  }
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

.submit-button:hover:not(:disabled) {
  background-color: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
}

.submit-button:active {
  transform: translateY(0);
}

.submit-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.order-preview {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.order-preview h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-dark);
  margin: 0;
}

.preview-section {
  padding: 16px;
  background-color: #f8fafc;
  border-radius: 12px;
}

.preview-section h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-dark);
  margin: 0 0 12px 0;
}

.preview-section p {
  margin: 8px 0;
  color: var(--text-muted);
}

.product-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #e2e8f0;
}

.product-item:last-child {
  border-bottom: none;
}

.total-sum {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 2px solid var(--primary-color);
  text-align: right;
  font-size: 1.1rem;
}

.preview-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.secondary-button {
  padding: 16px;
  background-color: white;
  color: var(--primary-color);
  border: 2px solid var(--primary-color);
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.secondary-button:hover {
  background-color: #f1f5f9;
}
</style>
