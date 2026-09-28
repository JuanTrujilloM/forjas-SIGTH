<script setup lang="ts">
import type { EmployeeInfoRow } from '@/types/employee.types'

defineProps<{
  title: string
  rows: EmployeeInfoRow[]
  wide?: boolean
  highlight?: boolean
}>()
</script>

<template>
  <section class="card border-0 shadow-sm h-100" :class="{ 'info-card--highlight': highlight }">
    <div class="card-body">
      <h2 class="h6 text-uppercase text-secondary fw-semibold mb-3 info-card__title">
        {{ title }}
      </h2>

      <div class="d-flex flex-column flex-md-row gap-4">
        <slot name="aside" />

        <dl
          class="row g-3 mb-0 flex-grow-1 align-content-start"
          :class="wide ? 'row-cols-1 row-cols-sm-2 row-cols-lg-4' : 'row-cols-1 row-cols-sm-2'"
        >
          <div v-for="row in rows" :key="row.label" class="col" :class="{ 'w-100': row.multiline }">
            <dt class="small text-secondary fw-normal mb-1">{{ row.label }}</dt>
            <dd class="mb-0 text-break">
              <span v-if="row.badge" class="badge rounded-pill" :class="`text-bg-${row.badge}`">
                {{ row.value }}
              </span>
              <span
                v-else
                :class="[
                  row.isEmpty ? 'text-body-tertiary' : 'fw-medium',
                  { 'info-card__multiline': row.multiline },
                ]"
              >
                {{ row.value }}
              </span>
              <span
                v-if="row.hint"
                class="d-block small"
                :class="row.tone ? `text-${row.tone}-emphasis fw-medium` : 'text-secondary'"
              >
                {{ row.hint }}
              </span>
            </dd>
          </div>
        </dl>
      </div>

      <slot />
    </div>
  </section>
</template>

<style scoped>
.info-card__title {
  letter-spacing: 0.04em;
}

.info-card__multiline {
  white-space: pre-line;
}

.info-card--highlight {
  border-left: 4px solid var(--fb-orange) !important;
}
</style>
