import { createRouter, createWebHistory } from 'vue-router'

import { useSessionStore } from '@/stores/session'
import EmployeeDetailView from '@/views/EmployeeDetailView.vue'
import EmployeeFormView from '@/views/EmployeeFormView.vue'
import EmployeeListView from '@/views/EmployeeListView.vue'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'

// main code
const routes = [
  { path: '/', redirect: { name: 'home' } },
  { path: '/ingreso', name: 'login', component: LoginView },
  { path: '/inicio', name: 'home', component: HomeView, meta: { requiresAuth: true } },
  {
    path: '/empleados',
    name: 'employees',
    component: EmployeeListView,
    meta: { requiresAuth: true },
  },
  {
    path: '/empleados/nuevo',
    name: 'employee-create',
    component: EmployeeFormView,
    meta: { requiresAuth: true, requiresEditor: true },
  },
  {
    path: '/empleados/:id(\\d+)',
    name: 'employee-detail',
    component: EmployeeDetailView,
    meta: { requiresAuth: true },
  },
  {
    path: '/empleados/:id(\\d+)/editar',
    name: 'employee-edit',
    component: EmployeeFormView,
    meta: { requiresAuth: true, requiresEditor: true },
  },
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

  // interface convenience only: the backend refuses the write anyway (8.3)
  if (to.meta.requiresEditor && !session.user?.can_edit_employees) {
    return { name: 'employees' }
  }

  return true
})

export default router
