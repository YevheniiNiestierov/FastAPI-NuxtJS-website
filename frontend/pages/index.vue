<template>
  <div></div>
</template>

<script setup>
definePageMeta({
  middleware: [
    function () {
      return navigateTo('/products', { redirectCode: 301 });
    }
  ]
});
</script>
