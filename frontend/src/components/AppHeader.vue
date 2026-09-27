<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import forjasLogo from '@/assets/images/forjas-logo.svg'
import BaseService from '@/shared/services/BaseService'
import { useSessionStore } from '@/stores/session'

const route = useRoute()
const router = useRouter()
const session = useSessionStore()

const isLoggingOut = ref(false)
const errorMessage = ref<string | null>(null)

const isEmployeesSection = computed<boolean>(() => route.path.startsWith('/empleados'))

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
  <!-- dark on purpose: the logo is white, drawn for the login's photo background -->
  <header class="bg-primary" data-bs-theme="dark">
    <nav class="navbar navbar-expand container">
      <RouterLink class="navbar-brand" :to="{ name: 'home' }">
        <img :src="forjasLogo" alt="Forjas Bolívar" height="28" />
      </RouterLink>

      <ul class="navbar-nav me-auto">
        <li class="nav-item">
          <RouterLink class="nav-link" :to="{ name: 'home' }" exact-active-class="active">
            Inicio
          </RouterLink>
        </li>

        <li class="nav-item">
          <RouterLink
            class="nav-link"
            :class="{ active: isEmployeesSection }"
            :to="{ name: 'employees' }"
          >
            Empleados
          </RouterLink>
        </li>
      </ul>

      <span class="navbar-text small me-3 d-none d-md-inline">
        {{ session.user?.full_name }} · {{ session.user?.profile_name || 'Sin perfil' }}
      </span>

      <button class="btn btn-outline-light btn-sm" :disabled="isLoggingOut" @click="logout">
        {{ isLoggingOut ? 'Cerrando sesión…' : 'Cerrar sesión' }}
      </button>
    </nav>

    <div v-if="errorMessage" class="container">
      <div class="alert alert-danger mt-2" role="alert">{{ errorMessage }}</div>
    </div>
  </header>
</template>
