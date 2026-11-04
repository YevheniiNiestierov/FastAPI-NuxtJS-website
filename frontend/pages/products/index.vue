<template>
  <div></div>
</template>
<script setup>
// Old catalog URL: permanently redirect to /
definePageMeta({
  middleware: [
    function () {
      return navigateTo('/', { redirectCode: 301 });
    }
  ]
});
</script>
