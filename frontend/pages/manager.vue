<template>
  <h1>MANAGER VIEW</h1>
  <header class="about-header">
      <NuxtLink to="/products" class="back-link">← Повернутись до магазину</NuxtLink>
    </header>
  <div>
    <h1>Create Product</h1>
    <form @submit.prevent="createProduct">
      <label for="title">Title:</label>
      <input type="text" id="title" v-model="product.title" required>

      <label for="description">Description:</label>
      <textarea id="description" v-model="product.description" required></textarea>

      <label for="instructions">Instructions (optional):</label>
      <textarea id="instructions" v-model="product.instructions"></textarea>

      <label for="price">Price:</label>
      <input type="number" id="price" v-model.number="product.price" required>

      <label for="flavour">Flavour:</label>
      <select id="flavour" v-model="product.flavour" required>
        <option v-for="(flavour, index) in flavours" :key="index" :value="flavour">{{ flavour }}</option>
      </select>
      <div class="add-option-row">
        <input type="text" v-model="newFlavour" placeholder="Add new flavour…" />
        <button type="button" @click="addFlavour" :disabled="!newFlavour.trim()">+ Add</button>
      </div>

      <label for="type">Type:</label>
      <select id="type" v-model="product.product_type" required>
        <option v-for="(type, index) in types" :key="index" :value="type">{{ type }}</option>
      </select>
      <div class="add-option-row">
        <input type="text" v-model="newType" placeholder="Add new type…" />
        <button type="button" @click="addType" :disabled="!newType.trim()">+ Add</button>
      </div>

      <label for="weight">Weight:</label>
      <input type="number" id="weight" v-model.number="product.weight" required>

      <div class="image-upload-section">
        <label>Images (in display order):</label>
        <input type="file" multiple accept="image/jpeg,image/png,image/heic" @change="onFilesSelected" />
        <div v-if="selectedFiles.length" class="image-preview-list">
          <div
            v-for="(item, index) in selectedFiles"
            :key="item.id"
            class="image-preview-item"
          >
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

      <button type="submit">Create Product</button>
    </form>
  </div>
  <div>
    <h2>All Products</h2>
    <ul>
      <li v-for="p in products" :key="p.id">
        {{ p.title }} - {{ p.price }} грн.
        <button @click="startEdit(p)">Edit</button>
        <button @click="confirmDelete(p)" class="remove-btn">Delete</button>
      </li>
    </ul>
  </div>

  <!-- Edit Modal -->
  <div v-if="editingProduct" class="modal-overlay" @click.self="cancelEdit">
    <div class="modal">
      <h2>Edit Product</h2>
      <form @submit.prevent="saveEdit">
        <label>Title:</label>
        <input type="text" v-model="editingProduct.title" required />

        <label>Description:</label>
        <textarea v-model="editingProduct.description" required></textarea>

        <label>Instructions (optional):</label>
        <textarea v-model="editingProduct.instructions"></textarea>

        <label>Price:</label>
        <input type="number" v-model.number="editingProduct.price" required />

        <label>Flavour:</label>
        <select v-model="editingProduct.flavour" required>
          <option v-for="(f, i) in flavours" :key="i" :value="f">{{ f }}</option>
        </select>

        <label>Type:</label>
        <select v-model="editingProduct.product_type" required>
          <option v-for="(t, i) in types" :key="i" :value="t">{{ t }}</option>
        </select>

        <label>Weight:</label>
        <input type="number" v-model.number="editingProduct.weight" required />

        <div class="modal-actions">
          <button type="submit" class="save-btn">Save</button>
          <button type="button" @click="cancelEdit">Cancel</button>
        </div>
        <p v-if="editStatus" class="upload-status">{{ editStatus }}</p>
      </form>
    </div>
  </div>
  <!-- Delete Confirmation Modal -->
  <div v-if="deletingProduct" class="modal-overlay" @click.self="cancelDelete">
    <div class="modal">
      <h2>Delete Product</h2>
      <p>Are you sure you want to delete <strong>{{ deletingProduct.title }}</strong>?</p>
      <div class="modal-actions">
        <button class="remove-btn save-btn" style="background:#c00;" @click="confirmDeleteExecute">Delete</button>
        <button type="button" @click="cancelDelete">Cancel</button>
      </div>
    </div>
  </div>

  <div>
    <NuxtLink to="/products" class="products-button">Products Page</NuxtLink>
    <NuxtPage />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useFetch, useRuntimeConfig, navigateTo } from '#app';

const config = useRuntimeConfig();

// Check if user is admin
const checkAdminAccess = async () => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    navigateTo('/login');
    return;
  }
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    if (!payload.is_admin) throw new Error('Not admin');
  } catch {
    localStorage.removeItem('access_token');
    navigateTo('/login');
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

const confirmDelete = (p) => { deletingProduct.value = p; };
const cancelDelete = () => { deletingProduct.value = null; };
const confirmDeleteExecute = async () => {
  const id = deletingProduct.value.id;
  deletingProduct.value = null;
  await deleteProduct(id);
};

const startEdit = (p) => {
  editingProduct.value = { ...p };
  editStatus.value = '';
};

const cancelEdit = () => {
  editingProduct.value = null;
  editStatus.value = '';
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
    editStatus.value = '✓ Saved!';
    await getProducts();
    setTimeout(() => { editingProduct.value = null; editStatus.value = ''; }, 800);
  } catch (error) {
    console.error('Error updating product:', error);
    editStatus.value = '✗ Failed to save.';
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
    const { data } = await useFetch(`${config.public.apiBase}/image/images/upload`, {
      params: { filename, contentType: file.type }
    });
    return data.value;
  } catch (error) {
    console.error('Error getting pre-signed URL:', error);
    throw error;
  }
};

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
    const ext = file.name.split('.').pop() || 'jpg';
    const filename = `${title}_${i + 1}.${ext}`;
    await uploadFile(file, filename);
    uploadStatus.value = `Uploading ${i + 1} / ${selectedFiles.value.length}...`;
  }
  uploadStatus.value = `✓ ${selectedFiles.value.length} image(s) uploaded.`;
};

const token = localStorage.getItem('access_token');

const getFlavours = async () => {
  try {
    const { data } = await useFetch(`${config.public.apiBase}/product/flavours/`);
    flavours.value = data.value.flavours;
  } catch (error) {
    console.error('Error fetching flavours:', error);
  }
};

const getTypes = async () => {
  try {
    const { data } = await useFetch(`${config.public.apiBase}/product/types/`);
    types.value = data.value.types;
  } catch (error) {
    console.error('Error fetching types:', error);
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
    console.error('Error adding type:', error);
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
    console.error('Error adding flavour:', error);
  }
};

const getProducts = async () => {
  try {
    const { data } = await useFetch(`${config.public.apiBase}/product/products`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    products.value = data.value;
  } catch (error) {
    console.error('Error fetching products:', error);
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
    // Upload images named after the product title
    await uploadAllImages(product.value.title);
    selectedFiles.value = [];
    await getProducts();
  } catch (error) {
    console.error('Error creating product:', error);
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
    await getProducts(); // Refresh the product list
  } catch (error) {
    console.error('Error deleting product:', error);
  }
};


onMounted(() => {
  checkAdminAccess();
  getFlavours();
  getTypes();
  getProducts();
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

.products-button {
  display: inline-block;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  background-color: #42b983;
  color: white;
  font-size: 16px;
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.3s;
}

.products-button:hover {
  background-color: #369b74;
}

.image-upload-section {
  margin: 15px 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
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
  min-width: 24px;
  text-align: center;
  color: #753BBD;
}

.preview-thumb {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.file-name {
  flex: 1;
  font-size: 0.85rem;
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

.add-option-row {
  display: flex;
  gap: 8px;
  margin-top: 6px;
  margin-bottom: 12px;
}

.add-option-row input {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.9rem;
}

.add-option-row button {
  padding: 6px 12px;
  background: #753BBD;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  white-space: nowrap;
}

.add-option-row button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal {
  background: #fff;
  border-radius: 8px;
  padding: 28px 32px;
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}

.modal h2 {
  margin: 0 0 20px;
  font-size: 1.3rem;
  color: #333;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 18px;
}

.save-btn {
  padding: 10px 20px;
  background: #753BBD;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.save-btn:hover {
  background: #984ABD;
}

.modal-actions button[type="button"] {
  padding: 10px 20px;
  background: #eee;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}

.back-link {
  color: #753BBD;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
}
</style>
