<script setup>
// Catch-all: unknown URLs (e.g. bot probes for /.env) get a real 404 instead of a router warning.
throw createError({ statusCode: 404, statusMessage: 'Сторінку не знайдено', fatal: true });
</script>

<template>
  <div></div>
</template>

