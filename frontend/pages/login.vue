<template>
  <div class="login-container">
    <h1>Admin Login</h1>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">Email:</label>
        <input type="email" id="username" v-model="credentials.username" required>
      </div>

      <div class="form-group">
        <label for="password">Password:</label>
        <input type="password" id="password" v-model="credentials.password" required>
      </div>

      <button type="submit" class="submit-button">Login</button>

      <div v-if="sessionExpired" class="session-message">Your session has expired. Please log in again.</div>
      <div v-if="error" class="error-message">{{ error }}</div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRuntimeConfig, navigateTo, useRoute } from '#app';

const config = useRuntimeConfig();
const route = useRoute();
const credentials = ref({ username: '', password: '' });
const error = ref('');
const sessionExpired = ref(false);

onMounted(() => {
  if (route.query.session === 'expired') sessionExpired.value = true;
});

const handleLogin = async () => {
  try {
    const response = await fetch(`${config.public.apiBase}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams(credentials.value)
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    navigateTo('/manager');
  } catch (err) {
    error.value = 'Invalid credentials';
  }
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border-radius: 8px;
  background-color: #f9f9f9;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.submit-button {
  width: 100%;
  padding: 10px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.error-message {
  color: red;
  margin-top: 10px;
}

.session-message {
  color: #b85c00;
  background: #fff3e0;
  border: 1px solid #ffcc80;
  border-radius: 4px;
  padding: 8px 12px;
  margin-top: 10px;
  font-size: 0.9rem;
}
</style>
