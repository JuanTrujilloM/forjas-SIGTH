<script setup lang="ts">
import { computed } from 'vue'

import AppHeader from '@/components/AppHeader.vue'
import { useSessionStore } from '@/stores/session'

const session = useSessionStore()

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
    ? `Ves los empleados de las secciones: ${user.section_names.join(', ')}.`
    : 'Tu cuenta no tiene secciones a cargo asignadas.'
})
</script>

<template>
  <AppHeader />

  <main class="container py-5">
    <h1 class="h3 mb-1">Hola, {{ session.user?.full_name }}</h1>

    <p class="text-secondary mb-1">Perfil: {{ session.user?.profile_name || 'Sin perfil' }}</p>

    <p class="text-secondary">{{ scopeDescription }}</p>

    <RouterLink v-if="session.user?.profile" class="btn btn-primary" :to="{ name: 'employees' }">
      Ver empleados
    </RouterLink>
  </main>
</template>
