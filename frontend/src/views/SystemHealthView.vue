<script setup lang="ts">
import { onMounted, ref } from 'vue'

import SystemService from '@/services/SystemService'
import type { SystemHealth } from '@/types/system.types'

const health = ref<SystemHealth | null>(null)
const errorMessage = ref<string | null>(null)
const isLoading = ref(false)

async function checkConnection(): Promise<void> {
  isLoading.value = true
  health.value = null
  errorMessage.value = null

  try {
    health.value = await SystemService.getHealth()
  } catch (error) {
    errorMessage.value = SystemService.getApiErrorMessage(error, 'No se pudo comprobar la conexión.')
  } finally {
    isLoading.value = false
  }
}

onMounted(checkConnection)
</script>

<template>
  <main class="container py-5">
    <h1 class="h3 mb-4">Estado de la conexión</h1>

    <p v-if="isLoading" class="text-secondary">Consultando la API…</p>

    <div v-else-if="health" class="alert alert-success" role="status">
      <strong>Conexión correcta.</strong>
      La API respondió <code>{{ health.status }}</code> desde {{ health.service }}.
    </div>

    <div v-else-if="errorMessage" class="alert alert-danger" role="alert">
      <strong>Sin conexión.</strong>
      {{ errorMessage }}
    </div>

    <button class="btn btn-primary" :disabled="isLoading" @click="checkConnection">
      Volver a comprobar
    </button>
  </main>
</template>
