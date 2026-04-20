<template>
  <div class="about-wrapper">
    <header class="about-header">
      <NuxtLink to="/customer" class="back-link">← Повернутись до магазину</NuxtLink>
    </header>

    <main class="about-content">
      <section class="brand-section">
        <img src="/natur_savon_logo.png" alt="Natur Savon Logo" class="brand-image" />
      </section>

      <section class="about-card">
        <h1 class="about-title">Про нас</h1>
        <p class="about-text">
          Ласкаво просимо до <strong>Natur Savon</strong> — бренду натурального мила та косметики ручної роботи.
        </p>
        <p class="about-text">
          Ми створюємо продукцію з любов'ю до природи та піклуванням про вашу шкіру. Кожен наш виріб виготовляється
          вручну з натуральних інгредієнтів без шкідливих хімічних добавок.
        </p>
        <p class="about-text">
          Наша місія — допомогти вам доглядати за собою екологічно та свідомо, насолоджуючись ароматами та
          властивостями природних компонентів.
        </p>
      </section>

      <section class="values-section">
        <div class="value-card">
          <span class="value-icon">🌿</span>
          <h3>Натуральність</h3>
          <p>Тільки природні інгредієнти без парабенів та SLS</p>
        </div>
        <div class="value-card">
          <span class="value-icon">🤲</span>
          <h3>Ручна робота</h3>
          <p>Кожен виріб виготовлений вручну з особливою увагою</p>
        </div>
        <div class="value-card">
          <span class="value-icon">♻️</span>
          <h3>Екологічність</h3>
          <p>Екологічне пакування та відповідальне виробництво</p>
        </div>
      </section>

      <section class="about-card">
        <h2 class="about-subtitle">Наші контакти</h2>
        <p class="about-text">📧 Email: <a href="mailto:natursavon@gmail.com" class="contact-link">natursavon@gmail.com</a></p>
        <p class="about-text">📱 Instagram: <a href="https://instagram.com/natur_savon" target="_blank" class="contact-link">@natur_savon</a></p>
      </section>

      <div class="legal-link-section">
        <NuxtLink to="/contract" class="legal-link">📄 Публічний договір</NuxtLink>
      </div>
    </main>
  </div>
</template>

<script setup>
</script>

<style scoped>
.about-wrapper {
  font-family: 'Inter', -apple-system, sans-serif;
  background-color: #f8fafc;
  min-height: 100vh;
  padding: 40px 20px;
  color: #1e293b;
}

.about-header {
  max-width: 860px;
  margin: 0 auto 32px;
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

.about-content {
  max-width: 860px;
  margin: 0 auto;
}

.brand-section {
  max-width: 860px;
  margin: 0 auto 40px;
  text-align: center;
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.brand-image {
  max-width: 300px;
  height: auto;
  object-fit: contain;
}

@media (max-width: 768px) {
  .brand-image {
    max-width: 200px;
  }
  .brand-section {
    padding: 20px;
  }
}

.about-card {
  background: white;
  border-radius: 16px;
  padding: 36px 40px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08);
  margin-bottom: 28px;
}

.about-title {
  font-size: 2rem;
  font-weight: 800;
  margin: 0 0 20px;
  color: #753BBD;
}

.about-subtitle {
  font-size: 1.4rem;
  font-weight: 700;
  margin: 0 0 16px;
  color: #753BBD;
}

.about-text {
  font-size: 1rem;
  line-height: 1.75;
  color: #475569;
  margin-bottom: 14px;
}

.values-section {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 28px;
}

.value-card {
  background: white;
  border-radius: 16px;
  padding: 28px 24px;
  text-align: center;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08);
}

.value-icon {
  font-size: 2.4rem;
  display: block;
  margin-bottom: 12px;
}

.value-card h3 {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0 0 8px;
  color: #1e293b;
}

.value-card p {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0;
}

.contact-link {
  color: #753BBD;
  text-decoration: none;
  font-weight: 600;
}

.contact-link:hover {
  text-decoration: underline;
}

.legal-link-section {
  text-align: center;
  margin-top: 8px;
}

.legal-link {
  color: #753BBD;
  font-weight: 600;
  text-decoration: none;
  font-size: 1rem;
}

.legal-link:hover {
  text-decoration: underline;
}
</style>

