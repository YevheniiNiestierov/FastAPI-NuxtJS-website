<template>
  <div class="manager-page">
    <header class="page-header">
      <NuxtLink to="/products" class="back-link">← Повернутись до магазину</NuxtLink>
      <h1 class="page-title">Панель менеджера</h1>
    </header>

    <div class="manager-grid">
      <!-- Create Product -->
      <section class="card">
        <h2 class="card-title">Створити продукт</h2>
        <form @submit.prevent="createProduct" class="product-form">

          <div class="form-group">
            <label for="title">Назва:</label>
            <input type="text" id="title" v-model="product.title" required placeholder="Введіть назву продукту" />
          </div>

          <div class="form-group">
            <label for="description">Опис:</label>
            <textarea id="description" v-model="product.description" required placeholder="Введіть опис продукту"></textarea>
          </div>

          <div class="form-group">
            <label for="instructions">Інструкція (необов'язково):</label>
            <textarea id="instructions" v-model="product.instructions" placeholder="Введіть інструкцію"></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="price">Ціна (грн):</label>
              <input type="number" id="price" v-model.number="product.price" required placeholder="0" />
            </div>
            <div class="form-group">
              <label for="weight">Вага (г):</label>
              <input type="number" id="weight" v-model.number="product.weight" required placeholder="0" />
            </div>
          </div>

          <div class="form-group">
            <label for="flavour">Аромат:</label>
            <select id="flavour" v-model="product.flavour" required>
              <option value="" disabled>Оберіть аромат</option>
              <option v-for="(flavour, index) in flavours" :key="index" :value="flavour">{{ flavour }}</option>
            </select>
            <div class="add-option-row">
              <input type="text" v-model="newFlavour" placeholder="Додати новий аромат…" />
              <button type="button" @click="addFlavour" :disabled="!newFlavour.trim()">+ Додати</button>
            </div>
          </div>

          <div class="form-group">
            <label for="type">Тип:</label>
            <select id="type" v-model="product.product_type" required>
              <option value="" disabled>Оберіть тип</option>
              <option v-for="(type, index) in types" :key="index" :value="type">{{ type }}</option>
            </select>
            <div class="add-option-row">
              <input type="text" v-model="newType" placeholder="Додати новий тип…" />
              <button type="button" @click="addType" :disabled="!newType.trim()">+ Додати</button>
            </div>
          </div>

          <div class="form-group image-upload-section">
            <label>Зображення (у порядку відображення):</label>
            <input type="file" multiple accept="image/jpeg,image/png,image/heic" @change="onFilesSelected" />
            <div v-if="selectedFiles.length" class="image-preview-list">
              <div v-for="(item, index) in selectedFiles" :key="item.id" class="image-preview-item">
                <span class="order-badge">{{ index + 1 }}</span>
                <img :src="item.preview" class="preview-thumb" :alt="item.file.name" />
                <span class="file-name">{{ item.file.name }}</span>
                <div class="reorder-buttons">
                  <button type="button" :disabled="index === 0" @click="moveUp(index)">▲</button>
                  <button type="button" :disabled="index === selectedFiles.length - 1" @click="moveDown(index)">▼</button>
                </div>
                <button type="button" class="remove-btn" @click="removeFile(index)">✕</button>
              </div>
            </div>
            <p v-if="uploadStatus" class="upload-status">{{ uploadStatus }}</p>
          </div>

          <button type="submit" class="btn-primary">✓ Створити продукт</button>
        </form>
      </section>

      <!-- Product List -->
      <section class="card">
        <h2 class="card-title">Усі продукти</h2>
        <ul class="product-list">
          <li v-for="p in products" :key="p.id" class="product-list-item">
            <div class="product-info">
              <span class="product-name">{{ p.title }}</span>
              <span class="product-price">{{ p.price }} грн.</span>
            </div>
            <div class="product-actions">
              <button @click="startEdit(p)" class="btn-edit">✎ Редагувати</button>
              <button @click="confirmDelete(p)" class="btn-delete">✕ Видалити</button>
            </div>
          </li>
        </ul>
        <p v-if="!products.length" class="empty-list">Продуктів ще немає.</p>
      </section>
    </div>

    <!-- Edit Modal -->
    <div v-if="editingProduct" class="modal-overlay" @click.self="cancelEdit">
      <div class="modal">
        <h2>Редагувати продукт</h2>
        <form @submit.prevent="saveEdit" class="product-form">
          <div class="form-group">
            <label>Назва:</label>
            <input type="text" v-model="editingProduct.title" required />
          </div>
          <div class="form-group">
            <label>Опис:</label>
            <textarea v-model="editingProduct.description" required></textarea>
          </div>
          <div class="form-group">
            <label>Інструкція (необов'язково):</label>
            <textarea v-model="editingProduct.instructions"></textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Ціна (грн):</label>
              <input type="number" v-model.number="editingProduct.price" required />
            </div>
            <div class="form-group">
              <label>Вага (г):</label>
              <input type="number" v-model.number="editingProduct.weight" required />
            </div>
          </div>
          <div class="form-group">
            <label>Аромат:</label>
            <select v-model="editingProduct.flavour" required>
              <option v-for="(f, i) in flavours" :key="i" :value="f">{{ f }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Тип:</label>
            <select v-model="editingProduct.product_type" required>
              <option v-for="(t, i) in types" :key="i" :value="t">{{ t }}</option>
            </select>
          </div>

          <!-- Image management -->
          <div class="form-group image-upload-section">
            <label>Поточні зображення:</label>
            <div v-if="editImages.length" class="image-preview-list">
              <div v-for="(key, index) in editImages" :key="key" class="image-preview-item">
                <span class="order-badge">{{ index + 1 }}</span>
                <img
                  :src="`${config.public.apiBase}/image/images/${encodeURIComponent(key)}`"
                  class="preview-thumb"
                  :alt="key"
                />
                <span class="file-name">{{ key }}</span>
                <div class="reorder-buttons">
                  <button type="button" :disabled="index === 0" @click="moveEditExistingUp(index)">▲</button>
                  <button type="button" :disabled="index === editImages.length - 1" @click="moveEditExistingDown(index)">▼</button>
                </div>
                <button type="button" class="remove-btn" @click="removeEditExistingImage(key)">✕</button>
              </div>
            </div>
            <p v-else class="empty-list" style="padding:8px 0">Зображень немає.</p>

            <label style="margin-top:8px">Додати нові зображення:</label>
            <input type="file" multiple accept="image/jpeg,image/png,image/heic" @change="onEditFilesSelected" />
            <div v-if="editNewFiles.length" class="image-preview-list" style="margin-top:6px">
              <div v-for="(item, index) in editNewFiles" :key="item.id" class="image-preview-item">
                <span class="order-badge">{{ index + 1 }}</span>
                <img :src="item.preview" class="preview-thumb" :alt="item.file.name" />
                <span class="file-name">{{ item.file.name }}</span>
                <div class="reorder-buttons">
                  <button type="button" :disabled="index === 0" @click="moveEditUp(index)">▲</button>
                  <button type="button" :disabled="index === editNewFiles.length - 1" @click="moveEditDown(index)">▼</button>
                </div>
                <button type="button" class="remove-btn" @click="removeEditNewFile(index)">✕</button>
              </div>
            </div>
            <p v-if="editImageStatus" class="upload-status">{{ editImageStatus }}</p>
          </div>

          <div class="modal-actions">
            <button type="submit" class="btn-primary">✓ Зберегти</button>
            <button type="button" class="btn-secondary" @click="cancelEdit">Скасувати</button>
          </div>
          <p v-if="editStatus" class="upload-status">{{ editStatus }}</p>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="deletingProduct" class="modal-overlay" @click.self="cancelDelete">
      <div class="modal modal-sm">
        <h2>Видалити продукт</h2>
        <p>Ви впевнені, що хочете видалити <strong>{{ deletingProduct.title }}</strong>?</p>
        <div class="modal-actions">
          <button class="btn-danger" @click="confirmDeleteExecute">✕ Видалити</button>
          <button type="button" class="btn-secondary" @click="cancelDelete">Скасувати</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useFetch, useRuntimeConfig, navigateTo } from '#app';

const config = useRuntimeConfig();

// Check if user is admin
const checkAdminAccess = async () => {
  if (!process.client) return;
  const storedToken = localStorage.getItem('access_token');
  if (!storedToken) {
    navigateTo('/login');
    return;
  }
  try {
    const payload = JSON.parse(atob(storedToken.split('.')[1]));
    if (!payload.is_admin) throw new Error('Not admin');
    // Check expiry
    if (payload.exp && payload.exp * 1000 < Date.now()) throw new Error('Expired');
  } catch {
    localStorage.removeItem('access_token');
    navigateTo('/login?session=expired');
  }
};


const product = ref({
  product_type: '',
  title: '',
  description: '',
  instructions: '',
  price: null,
  flavour: '',
  weight: null
});

const types = ref([]);
const flavours = ref([]);
const products = ref([]);
const newType = ref('');
const newFlavour = ref('');
const selectedFiles = ref([]); // [{ id, file, preview }]
const uploadStatus = ref('');
const editingProduct = ref(null);
const editStatus = ref('');
const deletingProduct = ref(null);

// Edit modal — image management
const editImages = ref([]);         // existing S3 keys (without extension), current order
const editImagesOriginal = ref([]); // original order to detect changes
const editNewFiles = ref([]);       // new files queued for upload
const editImageStatus = ref('');

const confirmDelete = (p) => { deletingProduct.value = p; };
const cancelDelete = () => { deletingProduct.value = null; };
const confirmDeleteExecute = async () => {
  const id = deletingProduct.value.id;
  deletingProduct.value = null;
  await deleteProduct(id);
};

const startEdit = async (p) => {
  editingProduct.value = { ...p };
  editStatus.value = '';
  editImages.value = [];
  editNewFiles.value = [];
  editImageStatus.value = '';
  try {
    const keys = await $fetch(`${config.public.apiBase}/image/images/gallery/${encodeURIComponent(p.title)}`);
    editImages.value = keys; // array of keys without extension
    editImagesOriginal.value = [...keys];
  } catch (e) {
    console.error('Failed to load images', e);
  }
};

const cancelEdit = () => {
  editNewFiles.value.forEach(f => URL.revokeObjectURL(f.preview));
  editingProduct.value = null;
  editStatus.value = '';
  editImages.value = [];
  editImagesOriginal.value = [];
  editNewFiles.value = [];
  editImageStatus.value = '';
};

const saveEdit = async () => {
  try {
    const { id, ...fields } = editingProduct.value;
    await $fetch(`${config.public.apiBase}/product/products/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(fields)
    });
    // Reorder existing images if order changed
    const orderChanged = editImages.value.length !== editImagesOriginal.value.length ||
      editImages.value.some((k, i) => k !== editImagesOriginal.value[i]);
    if (orderChanged && editImages.value.length > 0) {
      await reorderEditImages();
    }
    await uploadEditImages(editingProduct.value.title);
    editStatus.value = '✓ Saved!';
    await getProducts();
    setTimeout(() => {
      editNewFiles.value.forEach(f => URL.revokeObjectURL(f.preview));
      editingProduct.value = null;
      editStatus.value = '';
      editImages.value = [];
      editImagesOriginal.value = [];
      editNewFiles.value = [];
      editImageStatus.value = '';
    }, 800);
  } catch (error) {
    if (!handleAuthError(error)) {
      console.error('Error updating product:', error);
      editStatus.value = '✗ Failed to save.';
    }
  }
};

let fileIdCounter = 0;

const onFilesSelected = (event) => {
  const files = Array.from(event.target.files);
  for (const file of files) {
    selectedFiles.value.push({
      id: ++fileIdCounter,
      file,
      preview: URL.createObjectURL(file)
    });
  }
  // Reset input so same files can be re-added if needed
  event.target.value = '';
};

const moveUp = (index) => {
  if (index === 0) return;
  const arr = selectedFiles.value;
  [arr[index - 1], arr[index]] = [arr[index], arr[index - 1]];
};

const moveDown = (index) => {
  const arr = selectedFiles.value;
  if (index === arr.length - 1) return;
  [arr[index], arr[index + 1]] = [arr[index + 1], arr[index]];
};

const removeFile = (index) => {
  URL.revokeObjectURL(selectedFiles.value[index].preview);
  selectedFiles.value.splice(index, 1);
};

const getPreSignedUrl = async (file, filename) => {
  try {
    const data = await $fetch(`${config.public.apiBase}/image/images/upload`, {
      params: { filename, contentType: file.type }
    });
    return data;
  } catch (error) {
    console.error('Error getting pre-signed URL:', error);
    throw error;
  }
};

/**
 * Convert any image file to a WebP Blob using Canvas.
 * Falls back to the original file if the browser cannot process it.
 */
const convertToWebP = (file, quality = 0.85) => new Promise((resolve) => {
  const img = new Image();
  const objectUrl = URL.createObjectURL(file);
  img.onload = () => {
    const canvas = document.createElement('canvas');
    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;
    canvas.getContext('2d').drawImage(img, 0, 0);
    URL.revokeObjectURL(objectUrl);
    canvas.toBlob(
      (blob) => resolve(blob ?? file),
      'image/webp',
      quality
    );
  };
  img.onerror = () => {
    URL.revokeObjectURL(objectUrl);
    resolve(file); // fallback to original
  };
  img.src = objectUrl;
});

const resizeImage = (file, maxWidth, maxHeight) => new Promise((resolve, reject) => {
  const image = new Image();
  image.src = URL.createObjectURL(file);
  image.onload = () => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    let width = image.width;
    let height = image.height;

    if (width > height) {
      if (width > maxWidth) {
        height *= maxWidth / width;
        width = maxWidth;
      }
    } else {
      if (height > maxHeight) {
        width *= maxHeight / height;
        height = maxHeight;
      }
    }

    canvas.width = width;
    canvas.height = height;

    ctx.drawImage(image, 0, 0, width, height);

    canvas.toBlob((blob) => {
      resolve(blob);
    }, 'image/jpeg');
  };
  image.onerror = error => reject(error);
});

const uploadToS3 = async (signedUrl, file) => {
  try {
    await fetch(signedUrl, {
      method: 'PUT',
      headers: { 'Content-Type': file.type || 'image/jpeg' },
      body: file
    });
    return signedUrl.split('?')[0];
  } catch (error) {
    console.error('Error uploading file to S3:', error);
    throw error;
  }
};

const uploadFile = async (file, filename) => {
  try {
    const preSignedUrl = await getPreSignedUrl(file, filename);
    const uploadedUrl = await uploadToS3(preSignedUrl.url, file);
    return uploadedUrl;
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  }
};

const uploadAllImages = async (title) => {
  if (!selectedFiles.value.length) return;
  uploadStatus.value = `Uploading 0 / ${selectedFiles.value.length}...`;
  for (let i = 0; i < selectedFiles.value.length; i++) {
    const { file } = selectedFiles.value[i];
    const webp = await convertToWebP(file);
    const filename = `${title}_${i + 1}.webp`;
    await uploadFile(webp, filename);
    uploadStatus.value = `Uploading ${i + 1} / ${selectedFiles.value.length}...`;
  }
  uploadStatus.value = `✓ ${selectedFiles.value.length} image(s) uploaded.`;
};

// ---- Edit modal image helpers ----

const removeEditExistingImage = async (key) => {
  try {
    await $fetch(`${config.public.apiBase}/image/images/${encodeURIComponent(key)}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    });
    editImages.value = editImages.value.filter(k => k !== key);
    editImagesOriginal.value = editImages.value.filter(k => k !== key);
  } catch (e) {
    console.error('Failed to delete image', e);
    editImageStatus.value = '✗ Failed to delete image.';
  }
};

const moveEditExistingUp = (index) => {
  if (index === 0) return;
  const arr = editImages.value;
  [arr[index - 1], arr[index]] = [arr[index], arr[index - 1]];
};

const moveEditExistingDown = (index) => {
  const arr = editImages.value;
  if (index === arr.length - 1) return;
  [arr[index], arr[index + 1]] = [arr[index + 1], arr[index]];
};

const reorderEditImages = async () => {
  try {
    editImageStatus.value = 'Reordering images...';
    const result = await $fetch(`${config.public.apiBase}/image/images/reorder`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ keys: editImages.value })
    });
    editImages.value = result.keys;
    editImagesOriginal.value = [...result.keys];
  } catch (e) {
    console.error('Failed to reorder images', e);
    editImageStatus.value = '✗ Failed to reorder images.';
    throw e;
  }
};

let editFileIdCounter = 0;

const onEditFilesSelected = (event) => {
  const files = Array.from(event.target.files);
  for (const file of files) {
    editNewFiles.value.push({ id: ++editFileIdCounter, file, preview: URL.createObjectURL(file) });
  }
  event.target.value = '';
};

const moveEditUp = (index) => {
  if (index === 0) return;
  const arr = editNewFiles.value;
  [arr[index - 1], arr[index]] = [arr[index], arr[index - 1]];
};

const moveEditDown = (index) => {
  const arr = editNewFiles.value;
  if (index === arr.length - 1) return;
  [arr[index], arr[index + 1]] = [arr[index + 1], arr[index]];
};

const removeEditNewFile = (index) => {
  URL.revokeObjectURL(editNewFiles.value[index].preview);
  editNewFiles.value.splice(index, 1);
};

const uploadEditImages = async (title) => {
  if (!editNewFiles.value.length) return;
  const startIndex = editImages.value.length + 1;
  editImageStatus.value = `Uploading 0 / ${editNewFiles.value.length}...`;
  for (let i = 0; i < editNewFiles.value.length; i++) {
    const { file } = editNewFiles.value[i];
    const webp = await convertToWebP(file);
    const filename = `${title}_${startIndex + i}.webp`;
    await uploadFile(webp, filename);
    editImageStatus.value = `Uploading ${i + 1} / ${editNewFiles.value.length}...`;
  }
  editImageStatus.value = `✓ ${editNewFiles.value.length} image(s) uploaded.`;
};

let token = '';

const handleAuthError = (error) => {
  const status = error?.response?.status ?? error?.status;
  if (status === 401 || status === 403) {
    if (process.client) localStorage.removeItem('access_token');
    navigateTo('/login?session=expired');
    return true;
  }
  return false;
};

const getFlavours = async () => {
  try {
    const data = await $fetch(`${config.public.apiBase}/product/flavours/`);
    flavours.value = data.flavours;
  } catch (error) {
    if (!handleAuthError(error)) console.error('Error fetching flavours:', error);
  }
};

const getTypes = async () => {
  try {
    const data = await $fetch(`${config.public.apiBase}/product/types/`);
    types.value = data.types;
  } catch (error) {
    if (!handleAuthError(error)) console.error('Error fetching types:', error);
  }
};

const addType = async () => {
  const name = newType.value.trim();
  if (!name) return;
  try {
    const data = await $fetch(`${config.public.apiBase}/product/types/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ name })
    });
    types.value = data.types;
    newType.value = '';
  } catch (error) {
    if (!handleAuthError(error)) console.error('Error adding type:', error);
  }
};

const addFlavour = async () => {
  const name = newFlavour.value.trim();
  if (!name) return;
  try {
    const data = await $fetch(`${config.public.apiBase}/product/flavours/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ name })
    });
    flavours.value = data.flavours;
    newFlavour.value = '';
  } catch (error) {
    if (!handleAuthError(error)) console.error('Error adding flavour:', error);
  }
};

const getProducts = async () => {
  try {
    const data = await $fetch(`${config.public.apiBase}/product/products`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    products.value = data;
  } catch (error) {
    if (!handleAuthError(error)) console.error('Error fetching products:', error);
  }
};

const createProduct = async () => {
  try {
    await useFetch(`${config.public.apiBase}/product/create_product/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(product.value)
    });
    console.log('Product created successfully!');
    await uploadAllImages(product.value.title);
    selectedFiles.value = [];
    await getProducts();
  } catch (error) {
    if (!handleAuthError(error)) console.error('Error creating product:', error);
  }
};

const deleteProduct = async (productId) => {
  try {
    await useFetch(`${config.public.apiBase}/product/products/${productId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    console.log('Product deleted successfully!');
    await getProducts();
  } catch (error) {
    if (!handleAuthError(error)) console.error('Error deleting product:', error);
  }
};


onMounted(() => {
  token = localStorage.getItem('access_token') ?? '';
  checkAdminAccess();
  getFlavours();
  getTypes();
  getProducts();
});
</script>

<style scoped>
.manager-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 16px 40px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 28px;
  padding-bottom: 16px;
  border-bottom: 2px solid #eee;
}

.page-title {
  font-size: 1.6rem;
  color: #333;
  margin: 0;
}

.back-link {
  color: #753BBD;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
  white-space: nowrap;
}

.back-link:hover {
  text-decoration: underline;
}

/* Grid layout */
.manager-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: start;
}

@media (max-width: 768px) {
  .manager-grid {
    grid-template-columns: 1fr;
  }
}

/* Cards */
.card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
  padding: 24px;
}

.card-title {
  font-size: 1.2rem;
  color: #444;
  margin: 0 0 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

/* Form */
.product-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

label {
  font-weight: 600;
  font-size: 0.9rem;
  color: #555;
}

input,
textarea,
select {
  width: 100%;
  padding: 9px 11px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

input:focus,
textarea:focus,
select:focus {
  outline: none;
  border-color: #753BBD;
}

textarea {
  min-height: 80px;
  resize: vertical;
}

/* Buttons */
.btn-primary {
  padding: 10px 20px;
  background: #753BBD;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  align-self: flex-start;
}

.btn-primary:hover { background: #984ABD; }

.btn-secondary {
  padding: 10px 20px;
  background: #eee;
  color: #333;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
}

.btn-secondary:hover { background: #ddd; }

.btn-danger {
  padding: 10px 20px;
  background: #c00;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-danger:hover { background: #a00; }

.btn-edit {
  padding: 6px 12px;
  background: #f0ebfa;
  color: #753BBD;
  border: 1px solid #c9b0e8;
  border-radius: 5px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-edit:hover { background: #e2d5f5; }

.btn-delete {
  padding: 6px 12px;
  background: #fdecea;
  color: #c00;
  border: 1px solid #f5c6c3;
  border-radius: 5px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-delete:hover { background: #fbd8d5; }

/* Product List */
.product-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.product-list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 7px;
  background: #fafafa;
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.product-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-price {
  font-size: 0.85rem;
  color: #753BBD;
  font-weight: 500;
}

.product-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.empty-list {
  text-align: center;
  color: #aaa;
  font-style: italic;
  padding: 20px 0;
}

/* Add option row */
.add-option-row {
  display: flex;
  gap: 8px;
  margin-top: 5px;
}

.add-option-row input {
  flex: 1;
}

.add-option-row button {
  padding: 8px 12px;
  background: #753BBD;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  white-space: nowrap;
}

.add-option-row button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Image Upload */
.image-upload-section {
  gap: 8px;
}

.image-preview-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.image-preview-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fafafa;
}

.order-badge {
  font-weight: bold;
  font-size: 1rem;
  min-width: 22px;
  text-align: center;
  color: #753BBD;
}

.preview-thumb {
  width: 52px;
  height: 52px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.file-name {
  flex: 1;
  font-size: 0.82rem;
  color: #555;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.reorder-buttons {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.reorder-buttons button {
  width: 28px;
  height: 22px;
  padding: 0;
  font-size: 0.75rem;
  cursor: pointer;
  border: 1px solid #ccc;
  border-radius: 3px;
  background: #fff;
}

.reorder-buttons button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.remove-btn {
  background: none;
  border: none;
  color: #c00;
  font-size: 1rem;
  cursor: pointer;
  padding: 0 4px;
}

.upload-status {
  font-size: 0.9rem;
  color: #369b74;
  font-weight: bold;
}

/* Modals */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 16px;
}

.modal {
  background: #fff;
  border-radius: 10px;
  padding: 28px 32px;
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}

.modal-sm {
  max-width: 420px;
}

.modal h2 {
  margin: 0 0 20px;
  font-size: 1.3rem;
  color: #333;
}

.modal p {
  color: #555;
  margin-bottom: 8px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  flex-wrap: wrap;
}
</style>
