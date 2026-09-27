<script setup lang="ts">
import type { EmployeeInfoRow } from '@/types/employee.types'

defineProps<{
  title: string
  rows: EmployeeInfoRow[]
  wide?: boolean
}>()
</script>

<template>
  <section class="card border-0 shadow-sm h-100">
    <div class="card-body">
      <h2 class="h6 text-uppercase text-secondary fw-semibold mb-3 info-card__title">
        {{ title }}
      </h2>

      <dl
        class="row g-3 mb-0"
        :class="wide ? 'row-cols-1 row-cols-sm-2 row-cols-lg-4' : 'row-cols-1 row-cols-sm-2'"
      >
        <div v-for="row in rows" :key="row.label" class="col">
          <dt class="small text-secondary fw-normal mb-1">{{ row.label }}</dt>
          <dd class="mb-0 text-break" :class="row.isEmpty ? 'text-body-tertiary' : 'fw-medium'">
            {{ row.value }}
          </dd>
        </div>
      </dl>

      <slot />
    </div>
  </section>
</template>

<style scoped>
.info-card__title {
  letter-spacing: 0.04em;
}
</style>
