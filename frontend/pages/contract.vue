<template>
  <div class="contract-wrapper">
    <header class="contract-header">
      <NuxtLink to="/customer" class="back-link">← Повернутись до магазину</NuxtLink>
      <NuxtLink to="/about" class="back-link">Про нас</NuxtLink>
    </header>

    <main class="contract-content">
      <h1 class="contract-title">Публічний договір</h1>
      <div class="pdf-container">
        <iframe
          src="/публічний_договір.pdf"
          class="pdf-frame"
          title="Публічний договір"
        ></iframe>
      </div>
      <div class="download-section">
        <a href="/публічний_договір.pdf" download class="download-btn">⬇ Завантажити PDF</a>
      </div>
    </main>
  </div>
</template>

<script setup>
</script>

<style scoped>
.contract-wrapper {
  font-family: 'Inter', -apple-system, sans-serif;
  background-color: #f8fafc;
  min-height: 100vh;
  padding: 40px 20px;
  color: #1e293b;
}

.contract-header {
  max-width: 960px;
  margin: 0 auto 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.back-link {
  color: #753BBD;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
}

.back-link:hover {
  text-decoration: underline;
}

.contract-content {
  max-width: 960px;
  margin: 0 auto;
}

.contract-title {
  font-size: 2rem;
  font-weight: 800;
  color: #753BBD;
  margin: 0 0 28px;
  text-align: center;
}

.pdf-container {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08);
  width: 100%;
  height: 80vh;
  min-height: 500px;
}

.pdf-frame {
  width: 100%;
  height: 100%;
  border: none;
  display: block;
}

.download-section {
  text-align: center;
  margin-top: 24px;
}

.download-btn {
  display: inline-block;
  background: #753BBD;
  color: white;
  text-decoration: none;
  padding: 12px 28px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  transition: background 0.2s;
}

.download-btn:hover {
  background: #984ABD;
}
</style>

