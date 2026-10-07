<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import forjasLogo from '@/assets/images/forjas-logo.svg'
import EmployeeService from '@/services/EmployeeService'
import BaseService from '@/shared/services/BaseService'
import { useSessionStore } from '@/stores/session'

const route = useRoute()
const router = useRouter()
const session = useSessionStore()

const isLoggingOut = ref(false)
const errorMessage = ref<string | null>(null)
const contractAlertCount = ref<number | null>(null)

const scopeDescription = computed<string>(() => {
  const user = session.user

  if (!user?.profile) {
    return 'Tu cuenta no tiene un perfil de acceso: no ve información de empleados.'
  }

  if (user.sees_every_employee) {
    return 'Ves la información de todos los empleados.'
  }

  if (user.profile === 'director') {
    return `Ves los empleados de la ${user.division_name ?? 'dirección asignada'}.`
  }

  return user.section_names.length
    ? `Ves los empleados de: ${user.section_names.join(', ')}.`
    : 'Tu cuenta no tiene secciones a cargo asignadas.'
})

// a failed count only hides the badge; the alerts page shows its own error
async function loadContractAlertCount(): Promise<void> {
  if (!session.user?.can_view_contract_alerts) {
    return
  }

  try {
    contractAlertCount.value = (await EmployeeService.getContractAlerts()).length
  } catch {
    contractAlertCount.value = null
  }
}

onMounted(loadContractAlertCount)

async function logout(): Promise<void> {
  isLoggingOut.value = true
  errorMessage.value = null

  try {
    await session.logout()
    await router.replace({ name: 'login' })
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudo cerrar la sesión.')
  } finally {
    isLoggingOut.value = false
  }
}
</script>

<template>
  <div class="sticky-top">
    <!-- dark on purpose: the logo is white, drawn for the login's photo background -->
    <header class="bg-primary" data-bs-theme="dark">
      <nav class="navbar navbar-expand container">
        <RouterLink class="navbar-brand" :to="{ name: 'employees' }">
          <img :src="forjasLogo" alt="Forjas Bolívar" height="28" />
        </RouterLink>

        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <RouterLink
              class="nav-link"
              :class="{ active: route.path.startsWith('/empleados') }"
              :to="{ name: 'employees' }"
            >
              Empleados
            </RouterLink>
          </li>
          <li v-if="session.user?.can_view_contract_alerts" class="nav-item">
            <RouterLink class="nav-link" active-class="active" :to="{ name: 'contract-alerts' }">
              Vencimientos
              <span
                v-if="contractAlertCount"
                class="badge rounded-pill text-bg-warning ms-1"
                :aria-label="`${contractAlertCount} contratos en alerta`"
              >
                {{ contractAlertCount }}
              </span>
            </RouterLink>
          </li>
        </ul>

        <button class="btn btn-outline-light btn-sm" :disabled="isLoggingOut" @click="logout">
          {{ isLoggingOut ? 'Cerrando sesión…' : 'Cerrar sesión' }}
        </button>
      </nav>
    </header>

    <div class="bg-light border-bottom">
      <div class="container d-flex flex-wrap column-gap-3 row-gap-1 py-2 small">
        <span class="fw-medium">{{ session.user?.full_name }}</span>
        <span>Perfil: {{ session.user?.profile_name || 'Sin perfil' }}</span>
        <span class="text-secondary">{{ scopeDescription }}</span>
      </div>
    </div>

    <div v-if="errorMessage" class="container">
      <div class="alert alert-danger mt-2" role="alert">{{ errorMessage }}</div>
    </div>
  </div>
</template>
