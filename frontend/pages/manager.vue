<template>
  <h1>MANAGER VIEW</h1>
  <div>
    <input type="file" ref="fileInput" @change="uploadFile($event.target.files[0])">
  </div>
  <div>
    <h1>Create Product</h1>
    <form @submit.prevent="createProduct">
      <label for="title">Title:</label>
      <input type="text" id="title" v-model="product.title" required>

      <label for="description">Description:</label>
      <textarea id="description" v-model="product.description" required></textarea>

      <label for="price">Price:</label>
      <input type="number" id="price" v-model.number="product.price" required>

      <label for="flavour">Flavour:</label>
      <select id="flavour" v-model="product.flavour" required>
        <option v-for="(flavour, index) in flavours" :key="index" :value="flavour">{{ flavour }}</option>
      </select>

      <label for="type">Type:</label>
      <select id="type" v-model="product.type" required>
        <option v-for="(type, index) in types" :key="index" :value="type">{{ type }}</option>
      </select>

      <label for="weight">Weight:</label>
      <input type="number" id="weight" v-model.number="product.weight" required>

      <button type="submit">Create Product</button>
    </form>
  </div>
  <div>
    <NuxtLink to="/CustomerView">Customer Page</NuxtLink>
    <NuxtPage />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useFetch, useRuntimeConfig } from '#app';

const config = useRuntimeConfig();

const product = ref({
  product_type: '',
  title: '',
  description: '',
  price: null,
  flavour: '',
  weight: null
});

const types = ref([]);
const flavours = ref([]);

const getPreSignedUrl = async (file) => {
  try {
    const { data } = await useFetch(`${config.public.apiBase}/image/images/upload`, {
      params: { filename: file.name, contentType: file.type }
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
      headers: { 'Content-Type': 'image/jpeg' },
      body: file
    });
    return signedUrl.split('?')[0];
  } catch (error) {
    console.error('Error uploading file to S3:', error);
    throw error;
  }
};

const uploadFile = async (file) => {
  try {
    const preSignedUrl = await getPreSignedUrl(file);
    const resizedImage = await resizeImage(file, 200, 200);
    const uploadedUrl = await uploadToS3(preSignedUrl.url, resizedImage);
    return uploadedUrl;
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  }
};

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

const createProduct = async () => {
  try {
    await useFetch(`${config.public.apiBase}/product/create_product/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(product.value)
    });
    console.log('Product created successfully!');
    // Optionally, you can redirect the user to another page after successful creation
    // navigateTo('/products');
  } catch (error) {
    console.error('Error creating product:', error);
  }
};

onMounted(() => {
  getFlavours();
  getTypes();
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
