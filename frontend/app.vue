<template>
  <div id="app">
    <NuxtPage />
    <footer class="site-footer">
      <div class="social-links">
        <a
          href="https://www.instagram.com/natur_savon"
          target="_blank"
          rel="noopener noreferrer"
          class="social-link"
          aria-label="Instagram"
        >
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
            <circle cx="12" cy="12" r="4" />
            <circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none" />
          </svg>
          <span>@natur_savon</span>
        </a>
        <a
          href="https://www.facebook.com/people/Natur-Savon/61556569705374/"
          target="_blank"
          rel="noopener noreferrer"
          class="social-link"
          aria-label="Facebook"
        >
          <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor" aria-hidden="true">
            <path d="M22 12a10 10 0 1 0-11.56 9.88v-6.99H7.9V12h2.54V9.8c0-2.5 1.49-3.89 3.77-3.89 1.09 0 2.23.2 2.23.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56V12h2.78l-.44 2.89h-2.34v6.99A10 10 0 0 0 22 12z" />
          </svg>
          <span>Natur Savon</span>
        </a>
      </div>
    </footer>
  </div>
</template>

<script setup>
// Site-wide entity markup (rendered in the SSR <head> on every page).
const siteUrl = useRuntimeConfig().public.siteUrl;

useHead({
  script: [
    {
      key: 'ld-store',
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@graph': [
          {
            '@type': ['Organization', 'Store'],
            '@id': `${siteUrl}/#organization`,
            name: 'Natur Savon',
            url: siteUrl,
            logo: `${siteUrl}/natur_savon_logo.png`,
            image: `${siteUrl}/natur_savon_logo.png`,
            description:
              'Natur Savon — інтернет-магазин натурального мила та косметики ручної роботи в Україні.',
            slogan: 'Натуральне мило та косметика ручної роботи',
            areaServed: 'UA',
            knowsLanguage: 'uk',
            currenciesAccepted: 'UAH',
            sameAs: [
              'https://www.instagram.com/natur_savon',
              'https://www.facebook.com/people/Natur-Savon/61556569705374/'
            ]
          },
          {
            '@type': 'WebSite',
            '@id': `${siteUrl}/#website`,
            url: siteUrl,
            name: 'Natur Savon',
            inLanguage: 'uk',
            publisher: { '@id': `${siteUrl}/#organization` }
          }
        ]
      })
    }
  ]
});
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  background-image: url('/background_image.webp');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
  min-height: 100vh;
}

.site-footer {
  padding: 24px 16px 32px;
}

.social-links {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 24px;
}

.social-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 999px;
  background-color: #ffffff;
  color: #1a252f;
  font-size: 16px;
  font-weight: 600;
  text-decoration: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
}

.social-link:hover {
  opacity: 0.7;
}
</style>
