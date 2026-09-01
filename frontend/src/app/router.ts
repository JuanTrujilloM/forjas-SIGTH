import { createRouter, createWebHistory } from 'vue-router'

import SystemHealthView from '@/views/SystemHealthView.vue'

// main code
const routes = [
  { path: '/', redirect: { name: 'systemHealth' } },
  { path: '/estado', name: 'systemHealth', component: SystemHealthView },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
