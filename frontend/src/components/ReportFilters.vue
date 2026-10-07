<script setup lang="ts">
import { computed } from 'vue'

import { useSessionStore } from '@/stores/session'
import type { CostCenter, EmployeeChoices } from '@/types/employee.types'
import type { CatalogItem } from '@/types/organization.types'
import type { ReportFilters } from '@/types/report.types'

const props = defineProps<{
  choices: EmployeeChoices
  divisions: CatalogItem[]
  sections: CatalogItem[]
  positions: CatalogItem[]
  costCenters: CostCenter[]
}>()

const filters = defineModel<ReportFilters>({ required: true })

const session = useSessionStore()

// main code
const CHOICE_FILTERS = [
  { key: 'status', label: 'Estado' },
  { key: 'category', label: 'Categoría' },
  { key: 'employment_type', label: 'Tipo de vinculación' },
  { key: 'contract_type', label: 'Tipo de contrato' },
  { key: 'evaluation_group', label: 'Grupo de evaluación' },
  { key: 'area', label: 'Área' },
  { key: 'sex', label: 'Sexo' },
] as const

const DATE_FILTERS = [
  { field: 'hire_date', label: 'Fecha de ingreso' },
  { field: 'contract_end_date', label: 'Fecha de vencimiento' },
  { field: 'retirement_date', label: 'Fecha de retiro' },
] as const

const choiceFilters = computed(() =>
  CHOICE_FILTERS.filter((filter) => session.canRead(filter.key) && props.choices[filter.key]),
)

const dateFilters = computed(() => DATE_FILTERS.filter((filter) => session.canRead(filter.field)))

function activeItems<T extends { is_active: boolean; id: number }>(
  items: T[],
  selected: number | null,
) {
  return items.filter((item) => item.is_active || item.id === selected)
}
</script>

<template>
  <div class="d-flex flex-column gap-2">
    <div>
      <label class="form-label small mb-1" for="report-search">Nombre o identificación</label>
      <input
        id="report-search"
        v-model="filters.search"
        class="form-control form-control-sm"
        type="search"
      />
    </div>

    <div v-if="session.canRead('division')">
      <label class="form-label small mb-1" for="report-division">Dirección</label>
      <select id="report-division" v-model="filters.division" class="form-select form-select-sm">
        <option :value="null">Todas</option>
        <option v-for="item in divisions" :key="item.id" :value="item.id">{{ item.name }}</option>
      </select>
    </div>

    <div v-if="session.canRead('section')">
      <label class="form-label small mb-1" for="report-section">Sección</label>
      <select id="report-section" v-model="filters.section" class="form-select form-select-sm">
        <option :value="null">Todas</option>
        <option v-for="item in sections" :key="item.id" :value="item.id">{{ item.name }}</option>
      </select>
    </div>

    <div v-if="session.canRead('position')">
      <label class="form-label small mb-1" for="report-position">Cargo actual</label>
      <select id="report-position" v-model="filters.position" class="form-select form-select-sm">
        <option :value="null">Todos</option>
        <option
          v-for="item in activeItems(positions, filters.position)"
          :key="item.id"
          :value="item.id"
        >
          {{ item.name }}
        </option>
      </select>
    </div>

    <div v-if="session.canRead('cost_center')">
      <label class="form-label small mb-1" for="report-cost-center">Centro de costos</label>
      <select
        id="report-cost-center"
        v-model="filters.cost_center"
        class="form-select form-select-sm"
      >
        <option :value="null">Todos</option>
        <option
          v-for="item in activeItems(costCenters, filters.cost_center)"
          :key="item.id"
          :value="item.id"
        >
          {{ item.code }} — {{ item.name }}
        </option>
      </select>
    </div>

    <div v-for="filter in choiceFilters" :key="filter.key">
      <label class="form-label small mb-1" :for="`report-${filter.key}`">{{ filter.label }}</label>
      <select
        :id="`report-${filter.key}`"
        v-model="filters[filter.key]"
        class="form-select form-select-sm"
      >
        <option value="">Todos</option>
        <option
          v-for="option in choices[filter.key]"
          :key="String(option.value)"
          :value="option.value"
        >
          {{ option.label }}
        </option>
      </select>
    </div>

    <div v-if="session.canRead('is_leader')">
      <label class="form-label small mb-1" for="report-is-leader">Es líder</label>
      <select id="report-is-leader" v-model="filters.is_leader" class="form-select form-select-sm">
        <option value="">Todos</option>
        <option value="true">Sí</option>
        <option value="false">No</option>
      </select>
    </div>

    <div v-for="filter in dateFilters" :key="filter.field">
      <span class="form-label small mb-1 d-block">{{ filter.label }}</span>
      <div class="input-group input-group-sm">
        <input
          v-model="filters[`${filter.field}_from`]"
          class="form-control"
          type="date"
          :aria-label="`${filter.label} desde`"
        />
        <input
          v-model="filters[`${filter.field}_to`]"
          class="form-control"
          type="date"
          :aria-label="`${filter.label} hasta`"
        />
      </div>
    </div>
  </div>
</template>
