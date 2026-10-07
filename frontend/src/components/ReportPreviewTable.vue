<script setup lang="ts">
import type { ReportPage } from '@/types/report.types'

defineProps<{ report: ReportPage; currentPage: number }>()

const emit = defineEmits<{ page: [page: number] }>()
</script>

<template>
  <div>
    <div v-if="report.count === 0" class="alert alert-secondary" role="status">
      No hay empleados que coincidan con los filtros.
    </div>

    <template v-else>
      <div class="table-responsive border rounded">
        <table class="table table-sm table-striped table-hover align-middle small mb-0">
          <thead class="table-light">
            <tr>
              <th v-for="column in report.columns" :key="column.key" scope="col">
                {{ column.label }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in report.results" :key="row.id">
              <td v-for="(value, index) in row.values" :key="index">
                <RouterLink
                  v-if="report.columns[index]?.key === 'full_name'"
                  :to="{ name: 'employee-detail', params: { id: row.id } }"
                >
                  {{ value }}
                </RouterLink>
                <template v-else>{{ value || '—' }}</template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <nav
        class="d-flex align-items-center justify-content-between mt-2"
        aria-label="Paginación de la vista previa"
      >
        <span class="text-secondary small">
          {{ report.count }} {{ report.count === 1 ? 'empleado' : 'empleados' }} · página
          {{ currentPage }}
        </span>

        <div class="btn-group">
          <button
            class="btn btn-outline-primary btn-sm"
            :disabled="!report.previous"
            @click="emit('page', currentPage - 1)"
          >
            Anterior
          </button>
          <button
            class="btn btn-outline-primary btn-sm"
            :disabled="!report.next"
            @click="emit('page', currentPage + 1)"
          >
            Siguiente
          </button>
        </div>
      </nav>
    </template>
  </div>
</template>
