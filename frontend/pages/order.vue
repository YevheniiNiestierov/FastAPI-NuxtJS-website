<template>
  <div class="checkout-wrapper">
    <div class="checkout-card">
      <header class="checkout-header">
        <NuxtLink to="/" class="back-link">
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
            <NuxtLink :to="`/products/${product.slug || product.id}`" class="product-name">{{ product.title }}</NuxtLink>
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

        <!-- Privacy Policy Checkbox -->
        <div class="privacy-group">
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="order.privacy_policy_accepted"
              required
              class="checkbox-input"
            >
            <span class="checkbox-text">
              Я даю згоду на обробку моїх персональних даних відповідно до Закону України «Про захист персональних даних» та погоджуюсь з
              <NuxtLink to="/privacy-policy" target="_blank" class="privacy-link">
                Політикою конфіденційності
              </NuxtLink>
            </span>
          </label>
        </div>

        <div class="form-actions">
          <button
            type="submit"
            class="submit-button"
            :disabled="cartItems.length === 0 || !order.privacy_policy_accepted"
          >
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
            <NuxtLink :to="`/products/${product.slug || product.id}`" class="product-link">
              {{ product.title }} × {{ product.quantity }}
            </NuxtLink>
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
import { useRuntimeConfig, navigateTo } from '#app';

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
  privacy_policy_accepted: false,
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
    const data = await $fetch(`${config.public.apiBase}/cart/cart-products-and_total-price`, {
      headers: {
        'Session-ID': sessionID.value
      }
    });

    if (data) {
      cartItems.value = data.products || [];
      cartTotal.value = data.total_sum || 0;
    }
  } catch (error) {
    console.error('Error fetching cart:', error);
  }
};

const increaseQuantity = async (productId) => {
  try {
    await $fetch(`${config.public.apiBase}/cart/add/${productId}`, {
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
    await $fetch(`${config.public.apiBase}/cart/delete/${productId}`, {
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
    await $fetch(`${config.public.apiBase}/cart/delete/${productId}`, {
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
    const data = await $fetch(`${config.public.apiBase}/order/preview_order/`, {
      method: 'POST',
      headers: {
        'Session-ID': sessionID.value,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(order.value)
    });

    orderPreview.value = data;
    showPreview.value = true;
  } catch (error) {
    console.error('Error previewing order:', error);
    alert('Помилка при перегляді замовлення');
  }
};

const confirmOrder = async () => {
  try {
    const response = await $fetch(`${config.public.apiBase}/order/create_order/`, {
      method: 'POST',
      headers: {
        'Session-ID': sessionID.value,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(order.value)
    });

    cartItems.value = [];
    cartTotal.value = 0;

    // Перенаправляємо на сторінку подяки з номером замовлення
    await navigateTo({
      path: '/thank-you',
      query: { order: response.order_number }
    });
  } catch (error) {
    console.error('Error creating order:', error);
    alert('Помилка при створенні замовлення');
  }
};

const getDeliveryTypes = async () => {
  try {
    const data = await $fetch(`${config.public.apiBase}/order/delivery_types/`);
    if (data) delivery_types.value = data.delivery_types;
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
/* Додайте ці стилі до існуючих стилів у order.vue */
.privacy-group {
  margin-top: 4px;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  cursor: pointer;
  font-weight: 400;
  font-size: 0.85rem;
  color: var(--text-muted);
  line-height: 1.4;
}

.checkbox-input {
  margin-top: 3px;
  width: 18px;
  height: 18px;
  accent-color: var(--primary-color);
  cursor: pointer;
  flex-shrink: 0;
}

.privacy-link {
  color: var(--primary-color);
  text-decoration: underline;
  font-weight: 500;
}

.privacy-link:hover {
  color: var(--primary-hover);
}
</style>