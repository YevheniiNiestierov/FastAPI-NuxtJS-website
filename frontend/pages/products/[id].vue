<template>
  <div class="page-wrapper">
    <header class="page-header">
      <NuxtLink to="/" class="back-link">← Повернутись до магазину</NuxtLink>
    </header>

    <div v-if="pending && !product" class="loading">
      Завантаження...
    </div>
    <div v-else-if="product" class="product-container">
        <div class="image-section">
          <img
            :src="mainImageUrl"
            :alt="product.title"
            fetchpriority="high"
            decoding="async"
            class="product-image"
          />
          <div v-if="imageGallery.length > 1" class="thumbnail-gallery">
            <img
              v-for="(imageObj, idx) in imageGallery"
              :key="imageObj.key"
              :src="getThumbnailUrl(imageObj)"
              :alt="`Thumbnail for ${product.title}`"
              :loading="idx === 0 ? 'eager' : 'lazy'"
              decoding="async"
              width="80"
              height="80"
              @click="setActiveImage(imageObj)"
              :class="{ active: activeImage?.key === imageObj.key }"
              class="thumbnail-image"
            />
          </div>
          <div v-if="formattedCharacteristics.length" class="characteristics-box">
            <h3 class="characteristics-title">Характеристики</h3>
            <dl class="characteristics-list">
              <div v-for="item in formattedCharacteristics" :key="item.label" class="characteristic-row">
                <dt class="char-label">{{ item.label }}</dt>
                <dd class="char-value">{{ item.value }}</dd>
              </div>
            </dl>
          </div>

          <div v-if="formattedIngredients.length" class="characteristics-box">
            <h3 class="characteristics-title">Склад</h3>
            <div class="characteristics-list">
              <div v-for="(ingredient, idx) in formattedIngredients" :key="idx" class="characteristic-row">
                <span class="char-value ingredient-item">{{ ingredient }}</span>
              </div>
            </div>
          </div>
        </div>

      <div class="info-section">
        <h1 class="product-title">{{ product.title }}</h1>
        <p class="product-desc">{{ product.description }}</p>

        <div v-if="product.instructions" class="product-instructions">
          <h3 class="instructions-title">Інструкція із застосування:</h3>
          <p class="instructions-text">{{ product.instructions }}</p>
        </div>

        <div class="purchase-block">
          <div class="price-and-weight">
            <p class="price">{{ product.price }} грн.</p>
            <p class="weight">{{ product.weight }} г.</p>
          </div>

          <div class="actions">
            <div class="quantity-wrapper">
              <button @click="decreaseQuantity" class="qty-btn" aria-label="Зменшити кількість">-</button>
              <input
                id="qty"
                type="number"
                v-model.number="selectedQuantity"
                min="1"
                class="quantity-input"
              />
              <button @click="increaseQuantity" class="qty-btn" aria-label="Збільшити кількість">+</button>
            </div>

            <button @click="addItemToCart" class="add-to-cart-button">
              Додати до кошика
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="cart-wrapper">
      <theCart />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from "vue";
import { useFetch, useRoute, useRuntimeConfig, useState } from "#app";

// Config & Route
const config = useRuntimeConfig();
const route = useRoute();
const productId = route.params.id;

const apiBase = useApiBase();

const fallbackImage = (title) => ({
  key: `${title}_1`,
  cdn_url: `${config.public.cdnBase}/${encodeURIComponent(`${title}_1.webp`)}`
});

// -- SSR data: product + image gallery are fetched on the server so they are in the raw HTML --
const { data: productData } = await useAsyncData(`product-${productId}`, async () => {
  let data;
  try {
    data = await $fetch(`${apiBase}/product/products/${productId}`);
  } catch (error) {
    return null;
  }
  let gallery = [];
  try {
    gallery = await $fetch(`${apiBase}/image/images/gallery/${encodeURIComponent(data.title)}`);
  } catch (error) {
    gallery = [];
  }
  if (!gallery || gallery.length === 0) {
    gallery = [fallbackImage(data.title)];
  }
  return { product: data, gallery };
});

if (!productData.value) {
  throw createError({ statusCode: 404, statusMessage: 'Товар не знайдено', fatal: true });
}

// Old id / non-canonical URL -> permanent redirect to the slug URL
if (productData.value.product.slug && productData.value.product.slug !== productId) {
  await navigateTo(`/products/${productData.value.product.slug}`, { replace: true, redirectCode: 301 });
}

// State
const product = ref(productData.value.product);
const selectedQuantity = ref(1); // Local state for input
const sessionID = ref(null);
const pending = ref(false);
const imageGallery = ref(productData.value.gallery);
const activeImage = ref(productData.value.gallery[0] ?? null);

// New methods for quantity control
const increaseQuantity = () => {
  selectedQuantity.value++;
};

const decreaseQuantity = () => {
  if (selectedQuantity.value > 1) {
    selectedQuantity.value--;
  }
};

// Global State (Shared with Cart)
const productsInCart = useState('productsInCart', () => []);
const totalPrice = useState('totalPrice', () => 0);

// Main image: 800px variant by default, original (max 1200px) for high-DPR screens.
// Thumbnails use the 200px variant (80px CSS @2x) instead of the full-size file.
// Both fall back to the original on the Worker when no variant exists.
const mainImageUrl = computed(() => activeImage.value?.cdn_url || '');
const mainImageSrcset = computed(() => {
  const url = mainImageUrl.value;
  return url ? `${imageSrcset(url, [480, 800])}, ${url} 1200w` : '';
});

const getThumbnailUrl = (imageObj) => imageWithWidth(imageObj?.cdn_url, 200);

const setActiveImage = (imageObj) => {
  activeImage.value = imageObj;
};


// -- API Methods --


const formattedIngredients = computed(() => {
  if (!product.value?.ingredients) return [];
  return product.value.ingredients
    .split(/\r?\n|,/)
    .map((item) => item.trim())
    .filter((item) => item.length > 0);
});


const addItemToCart = async () => {
  if (!sessionID.value) return;

  try {
    // Use product_id instead of id
    const productId = product.value.product_id || product.value.id;

    await $fetch(`${apiBase}/cart/add/${productId}`, {
      headers: { 'Session-ID': sessionID.value },
      params: { quantity: selectedQuantity.value }
    });

    await fetchProductsAndTotalSum();
    alert(`Товар "${product.value.title}" додано до кошика!`);
  } catch (error) {
    console.error('Error adding product to basket:', error);
  }
};

const formattedCharacteristics = computed(() => {
  if (!product.value?.characteristics) return [];
  const order = ['Вид', 'Вага', 'Призначення', 'Тип шкіри', 'Форма', 'Запах'];
  const chars = product.value.characteristics;

  return order
    .map((key) => {
      const val = chars[key];
      if (!val || (Array.isArray(val) && val.length === 0)) return null;
      return {
        label: key,
        value: Array.isArray(val) ? val.join(', ') : String(val).trim()
      };
    })
    .filter((item) => item && item.value.length > 0);
});

const fetchProductsAndTotalSum = async () => {
  try {
    const data = await $fetch(`${apiBase}/cart/cart-products-and_total-price`, {
      headers: { 'Session-ID': sessionID.value }
    });
    if (data) {
      // Handle both response formats
      if (Array.isArray(data)) {
        productsInCart.value = data[0] || [];
        totalPrice.value = data[1] || 0;
      } else {
        productsInCart.value = data.products || [];
        totalPrice.value = data.total_sum || 0;
      }
    }
  } catch (error) {
    console.error('Error fetching products in cart:', error);
  }
};



// -- SEO / GEO: title, description, canonical, Open Graph + Product/Offer JSON-LD --
const absoluteUrl = (url) => (url && url.startsWith('/') ? `${config.public.siteUrl}${url}` : url);

const seoDescription = computed(() => {
  const p = product.value;
  if (!p) return '';
  const text = `${p.title} — ${p.description || ''}`.replace(/\s+/g, ' ').trim();
  const tail = ` Ціна ${p.price} грн, вага ${p.weight} г. Натуральна косметика Natur Savon.`;
  return (text.length > 110 ? text.slice(0, 107) + '…' : text) + tail;
});

usePageSeo(() => ({
  title: `${product.value.title} — купити | Natur Savon`,
  description: seoDescription.value,
  image: absoluteUrl(imageGallery.value[0]?.cdn_url),
  type: 'product'
}));

useHead(() => {
  const p = product.value;
  const url = `${config.public.siteUrl}/products/${p.slug || productId}`;
  const chars = p.characteristics || {};
  const additionalProperty = Object.entries(chars)
    .filter(([, v]) => v && (!Array.isArray(v) || v.length))
    .map(([name, v]) => ({
      '@type': 'PropertyValue',
      name,
      value: Array.isArray(v) ? v.join(', ') : String(v)
    }));
  const ld = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    '@id': `${url}#product`,
    name: p.title,
    description: p.description,
    sku: String(p.id),
    url,
    image: imageGallery.value.map((i) => absoluteUrl(i.cdn_url)).filter(Boolean),
    category: p.product_type,
    brand: { '@type': 'Brand', name: 'Natur Savon' },
    weight: { '@type': 'QuantitativeValue', value: p.weight, unitCode: 'GRM', unitText: 'г' },
    offers: {
      '@type': 'Offer',
      url,
      price: p.price,
      priceCurrency: 'UAH',
      availability: 'https://schema.org/InStock',
      itemCondition: 'https://schema.org/NewCondition',
      seller: { '@id': `${config.public.siteUrl}/#organization` }
    }
  };
  if (p.ingredients) ld.material = p.ingredients.replace(/\s*\r?\n\s*/g, ', ');
  if (p.flavour) additionalProperty.push({ '@type': 'PropertyValue', name: 'Аромат', value: p.flavour });
  if (additionalProperty.length) ld.additionalProperty = additionalProperty;
  return {
    script: [{ key: 'ld-product', type: 'application/ld+json', innerHTML: JSON.stringify(ld) }]
  };
});

// -- Lifecycle --

onMounted(async () => {
  if (import.meta.client) {
    // Session Management (browser-only: localStorage / crypto)
    let storedSession = localStorage.getItem('sessionID');
    if (!storedSession) {
      storedSession = crypto.randomUUID();
      localStorage.setItem('sessionID', storedSession);
    }
    sessionID.value = storedSession;

    await fetchProductsAndTotalSum();
  }
});
</script>

<style scoped>
.page-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading {
  text-align: center;
  font-size: 1.2rem;
  padding: 50px;
  color: #666;
}

/* Flex Container for 2-Column Layout */
.product-container {
  display: flex;
  gap: 40px;
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  align-items: flex-start;
}

/* Left Column */
.image-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  min-height: 400px;
}

.product-image {
  max-width: 100%;
  max-height: 500px;
  object-fit: contain;
  border-radius: 8px;
}

.thumbnail-gallery {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}

.thumbnail-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.3s;
}

.thumbnail-image:hover {
  border-color: #ccc;
}

.thumbnail-image.active {
  border-color: #753BBD;
}


/* Right Column */
.info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.product-title {
  font-size: 2rem;
  margin-bottom: 10px;
  color: #333;
}

.product-desc {
  font-size: 1rem;
  line-height: 1.6;
  color: #555;
}

/* --- New Purchase Block Styles --- */
.purchase-block {
  background: #f4f4f4;
  padding: 20px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
  border: 1px solid #eaeaea;
}

.price-and-weight {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 15px;
}

.price {
  font-size: 1.8rem;
  font-weight: bold;
  color: #753BBD;
  margin: 0;
}

.weight {
  font-size: 1rem;
  color: #777;
  margin: 0;
}

.actions {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

/* Big Quantity Controls */
.quantity-wrapper {
  display: flex;
  align-items: center;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  overflow: hidden;
  height: 52px; /* Bigger height for easier tapping */
}

.qty-btn {
  background: #fff;
  border: none;
  color: #333;
  font-size: 1.5rem;
  width: 52px;
  height: 100%;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: background 0.2s;
}

.qty-btn:hover {
  background: #eaeaea;
}

.quantity-input {
  width: 60px;
  text-align: center;
  font-size: 1.1rem;
  font-weight: 600;
  border: none;
  border-left: 1px solid #ddd;
  border-right: 1px solid #ddd;
  height: 100%;
  box-sizing: border-box;
  -moz-appearance: textfield; /* Remove default arrows in Firefox */
  color: #333;
}

/* Remove default arrows in Chrome/Safari/Edge */
.quantity-input::-webkit-outer-spin-button,
.quantity-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.add-to-cart-button {
  background-color: #753BBD;
  color: white;
  padding: 0 24px;
  border: none;
  border-radius: 6px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.1s;
  flex-grow: 1;
  height: 52px; /* Match quantity controls height */
  display: flex;
  justify-content: center;
  align-items: center;
}

.add-to-cart-button:hover {
  background-color: #984ABD;
}

.add-to-cart-button:active {
  transform: scale(0.98);
}

.quantity-wrapper label {
  font-size: 0.9rem;
  color: #555;
}

.quantity-input {
  width: 80px;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  text-align: center;
  height: 48px; /* Match button height */
  box-sizing: border-box;
}

.cart-wrapper {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  max-width: 350px;
}

@media (max-width: 768px) {
  .cart-wrapper {
    top: 10px;
    right: 10px;
    max-width: 280px;
  }
}

.add-to-cart-button {
  background-color: #753BBD;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
  flex-grow: 1;
  height: 48px; /* Explicit height */
  box-sizing: border-box;
}

.add-to-cart-button:hover {
  background-color: #984ABD;
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .product-container {
    flex-direction: column;
  }

  .actions {
    flex-direction: column;
    align-items: stretch;
  }
}

.product-instructions {
  background: #fafafa;
  border-left: 3px solid #753BBD;
  padding: 12px 16px;
  border-radius: 4px;
}

.instructions-title {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 6px 0;
}

.instructions-text {
  font-size: 0.95rem;
  line-height: 1.5;
  color: #555;
  margin: 0;
  white-space: pre-line;
}

.characteristics-box {
  width: 100%;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eaeaea;
}

.characteristics-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px 0;
}

.characteristics-list {
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.characteristic-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 0.92rem;
  border-bottom: 1px dashed #e0e0e0;
  padding-bottom: 4px;
  gap: 12px;
}

.char-label {
  color: #666;
  font-weight: 500;
}

.char-value {
  color: #222;
  font-weight: 600;
  text-align: right;
  margin: 0;
}

.ingredient-item {
  text-align: right;
  width: 100%;
}

.back-link {
  color: #753BBD;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
  white-space: nowrap;
}

.page-header {
  display: flex;
  justify-content: flex-start;
  text-align: left;
}
</style>
