<template>
  <nav>
    <router-view></router-view>
<!--    <router-link to="/manager">Go Manager</router-link>-->
  </nav>
<!--  <CustomerView/>-->
</template>

<script setup>
// import CustomerView from './components/customer.vue'

// <!--export default {-->
// <!--  name: 'App',-->
// <!--  components: {-->
// <!--    CustomerView,-->
// <!--  }-->
// <!--}-->
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  background-image: url('/background_image.jpeg');
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
</style>
