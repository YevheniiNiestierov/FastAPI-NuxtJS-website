import type { RouterConfig } from '@nuxt/schema'

export default <RouterConfig> {
  // https://router.vuejs.org/api/interfaces/routeroptions.html#routes
  routes: (_routes) => [
    {
      name: 'home',
      path: '/',
      component: () => import('~/pages/customer.vue').then(r => r.default || r)
    },
      {
      name: 'home',
      path: '/',
      component: () => import('~/pages/order.vue').then(r => r.default || r)
    }
  ],
}
