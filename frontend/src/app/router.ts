import { createRouter, createWebHistory } from 'vue-router'

import { useSessionStore } from '@/stores/session'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'

// main code
const routes = [
  { path: '/', redirect: { name: 'home' } },
  { path: '/ingreso', name: 'login', component: LoginView },
  { path: '/inicio', name: 'home', component: HomeView, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach(async (to) => {
  const session = useSessionStore()

  if (!session.isRestored) {
    await session.restore()
  }

  if (to.meta.requiresAuth && !session.isAuthenticated) {
    return { name: 'login', query: { destino: to.fullPath } }
  }

  if (to.name === 'login' && session.isAuthenticated) {
    return { name: 'home' }
  }

  return true
})

export default router
