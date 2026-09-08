<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import BaseService from '@/shared/services/BaseService'
import { useSessionStore } from '@/stores/session'

const router = useRouter()
const session = useSessionStore()

const isLoading = ref(false)
const errorMessage = ref<string | null>(null)

async function logout(): Promise<void> {
  isLoading.value = true
  errorMessage.value = null

  try {
    await session.logout()
    await router.replace({ name: 'login' })
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudo cerrar la sesión.')
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <main class="container py-5">
    <h1 class="h3 mb-1">Hola, {{ session.user?.full_name }}</h1>

    <p class="text-secondary">
      <template v-if="session.user?.sees_every_division">
        Ves la información de todas las direcciones.
      </template>
      <template v-else-if="session.user?.division_name">
        Dirección: {{ session.user.division_name }}
      </template>
      <template v-else>Tu cuenta no está asociada a ninguna dirección.</template>
    </p>

    <div v-if="errorMessage" class="alert alert-danger" role="alert">{{ errorMessage }}</div>

    <div class="alert alert-secondary" role="status">
      La consulta de empleados todavía no está disponible.
    </div>

    <button class="btn btn-primary" :disabled="isLoading" @click="logout">
      {{ isLoading ? 'Cerrando sesión…' : 'Cerrar sesión' }}
    </button>
  </main>
</template>
