<script setup lang="ts">
// main code
const TABS = [
  { name: 'employees', label: 'Listado' },
  { name: 'org-chart', label: 'Organigrama' },
  { name: 'org-structure', label: 'Por dirección' },
]
</script>

<template>
  <nav class="nav nav-underline mb-3" aria-label="Directorio de empleados">
    <RouterLink
      v-for="tab in TABS"
      :key="tab.name"
      class="nav-link"
      exact-active-class="active"
      :to="{ name: tab.name }"
    >
      {{ tab.label }}
    </RouterLink>
  </nav>
</template>
