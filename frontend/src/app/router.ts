import { createRouter, createWebHistory } from 'vue-router'

import { useSessionStore } from '@/stores/session'
import ContractAlertsView from '@/views/ContractAlertsView.vue'
import EmployeeDetailView from '@/views/EmployeeDetailView.vue'
import EmployeeFormView from '@/views/EmployeeFormView.vue'
import EmployeeListView from '@/views/EmployeeListView.vue'
import LoginView from '@/views/LoginView.vue'

// main code
const routes = [
  { path: '/', redirect: { name: 'employees' } },
  { path: '/ingreso', name: 'login', component: LoginView },
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
  {
    path: '/vencimientos',
    name: 'contract-alerts',
    component: ContractAlertsView,
    meta: { requiresAuth: true, requiresContractAlerts: true },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior: (_to, _from, savedPosition) => savedPosition ?? { top: 0 },
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
    return { name: 'employees' }
  }

  // interface convenience only: the backend refuses the write anyway
  if (to.meta.requiresEditor && !session.user?.can_edit_employees) {
    return { name: 'employees' }
  }

  if (to.meta.requiresContractAlerts && !session.user?.can_view_contract_alerts) {
    return { name: 'employees' }
  }

  return true
})

export default router
