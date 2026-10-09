<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import AppHeader from '@/components/AppHeader.vue'
import IndicatorCard from '@/components/IndicatorCard.vue'
import EmployeeService from '@/services/EmployeeService'
import IndicatorService from '@/services/IndicatorService'
import OrganizationService from '@/services/OrganizationService'
import '@/shared/charts/chartSetup'
import BaseService from '@/shared/services/BaseService'
import { useSessionStore } from '@/stores/session'
import type { EmployeeChoices } from '@/types/employee.types'
import type {
  Indicator,
  IndicatorParams,
  IndicatorResponse,
  SummaryData,
} from '@/types/indicator.types'
import type { CatalogItem } from '@/types/organization.types'

const session = useSessionStore()

// main code
const CHOICE_FILTERS = [
  { key: 'area', label: 'Área' },
  { key: 'sex', label: 'Sexo' },
  { key: 'employment_type', label: 'Vinculación' },
  { key: 'category', label: 'Categoría' },
] as const

// the compare select keeps "automatic" apart from "no comparison"
const AUTOMATIC = '__auto__'

const result = ref<IndicatorResponse | null>(null)
const choices = ref<EmployeeChoices>({})
const divisions = ref<CatalogItem[]>([])
const sections = ref<CatalogItem[]>([])

const period = ref('actual')
const compare = ref(AUTOMATIC)
const filters = ref<Record<string, string>>({
  division: '',
  section: '',
  area: '',
  sex: '',
  employment_type: '',
  category: '',
})

const isLoading = ref(false)
const isDownloading = ref(false)
const errorMessage = ref<string | null>(null)

const choiceFilters = computed(() =>
  CHOICE_FILTERS.filter((filter) => session.canRead(filter.key) && choices.value[filter.key]),
)

const summary = computed<SummaryData | null>(() => {
  const indicator = result.value?.indicators.find((item) => item.kind === 'summary')
  return indicator?.kind === 'summary' ? indicator.data : null
})

const cards = computed(
  () =>
    (result.value?.indicators ?? []).filter((item) => item.kind !== 'summary') as Exclude<
      Indicator,
      { kind: 'summary' }
    >[],
)

const WIDE_KINDS = new Set(['line', 'table'])

const params = computed<IndicatorParams>(() => {
  const values: IndicatorParams = { period: period.value }

  if (compare.value !== AUTOMATIC) {
    values.compare = compare.value
  }

  for (const [key, value] of Object.entries(filters.value)) {
    if (value) {
      values[key] = value
    }
  }

  return values
})

function signed(value: number): string {
  return value > 0 ? `+${value}` : String(value)
}

async function load(): Promise<void> {
  isLoading.value = true
  errorMessage.value = null

  try {
    result.value = await IndicatorService.get(params.value)
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudo cargar la analítica.')
  } finally {
    isLoading.value = false
  }
}

async function download(): Promise<void> {
  isDownloading.value = true
  errorMessage.value = null

  try {
    await IndicatorService.downloadExcel(params.value)
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudo descargar la analítica.')
  } finally {
    isDownloading.value = false
  }
}

function clearFilters(): void {
  filters.value = Object.fromEntries(Object.keys(filters.value).map((key) => [key, '']))
}

watch(params, load, { deep: true })

onMounted(async () => {
  try {
    ;[choices.value, divisions.value, sections.value] = await Promise.all([
      EmployeeService.getChoices(),
      OrganizationService.getDivisions(),
      OrganizationService.getSections(),
    ])
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudieron cargar los filtros.')
  }

  await load()
})
</script>

<template>
  <AppHeader />

  <main class="container py-4">
    <div class="d-flex flex-wrap align-items-start justify-content-between gap-2 mb-1">
      <h1 class="h3 mb-0">Analítica de Talento Humano</h1>
      <button
        class="btn btn-outline-primary btn-sm"
        type="button"
        :disabled="isDownloading || !result?.indicators.length"
        @click="download"
      >
        {{ isDownloading ? 'Generando…' : 'Descargar Excel' }}
      </button>
    </div>
    <p class="text-secondary mb-3">
      Indicadores sobre los empleados de tu alcance. Un mes pasado sale de su corte mensual, tal
      como quedó al cierre.
    </p>

    <form class="row g-2 mb-3" @submit.prevent>
      <div class="col-6 col-md-3 col-xl-2">
        <label class="form-label small mb-1" for="period">Periodo</label>
        <select id="period" v-model="period" class="form-select form-select-sm">
          <option v-for="option in result?.periods ?? []" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </div>

      <div class="col-6 col-md-3 col-xl-2">
        <label class="form-label small mb-1" for="compare">Comparar con</label>
        <select id="compare" v-model="compare" class="form-select form-select-sm">
          <option :value="AUTOMATIC">El mes anterior</option>
          <option value="">Sin comparar</option>
          <option
            v-for="option in (result?.periods ?? []).filter((item) => item.value !== period)"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>
      </div>

      <div v-if="session.canRead('division')" class="col-6 col-md-3 col-xl-2">
        <label class="form-label small mb-1" for="filter-division">Dirección</label>
        <select id="filter-division" v-model="filters.division" class="form-select form-select-sm">
          <option value="">Todas</option>
          <option v-for="item in divisions" :key="item.id" :value="String(item.id)">
            {{ item.name }}
          </option>
        </select>
      </div>

      <div v-if="session.canRead('section')" class="col-6 col-md-3 col-xl-2">
        <label class="form-label small mb-1" for="filter-section">Sección</label>
        <select id="filter-section" v-model="filters.section" class="form-select form-select-sm">
          <option value="">Todas</option>
          <option v-for="item in sections" :key="item.id" :value="String(item.id)">
            {{ item.name }}
          </option>
        </select>
      </div>

      <div v-for="filter in choiceFilters" :key="filter.key" class="col-6 col-md-3 col-xl-2">
        <label class="form-label small mb-1" :for="`filter-${filter.key}`">{{
          filter.label
        }}</label>
        <select
          :id="`filter-${filter.key}`"
          v-model="filters[filter.key]"
          class="form-select form-select-sm"
        >
          <option value="">Todos</option>
          <option
            v-for="option in choices[filter.key]"
            :key="String(option.value)"
            :value="String(option.value)"
          >
            {{ option.label }}
          </option>
        </select>
      </div>

      <div class="col-6 col-md-3 col-xl-2 d-flex align-items-end">
        <button class="btn btn-link btn-sm px-0" type="button" @click="clearFilters">
          Limpiar filtros
        </button>
      </div>
    </form>

    <div v-if="errorMessage" class="alert alert-danger" role="alert">{{ errorMessage }}</div>

    <div v-if="isLoading && !result" class="text-secondary py-3" role="status">
      Calculando indicadores…
    </div>

    <div
      v-else-if="result && !result.indicators.length"
      class="alert alert-secondary"
      role="status"
    >
      Tu perfil no tiene indicadores para mostrar.
    </div>

    <div v-else-if="result" :class="{ 'opacity-50': isLoading }">
      <div v-if="summary" class="row g-3 mb-3">
        <div class="col-6 col-lg-3">
          <div class="card h-100">
            <div class="card-body">
              <div class="small text-secondary">Activos · {{ result.period.label }}</div>
              <div class="display-6 fw-semibold">{{ summary.active }}</div>
            </div>
          </div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="card h-100">
            <div class="card-body">
              <div class="small text-secondary">Ingresos de {{ summary.month }}</div>
              <div class="display-6 fw-semibold">{{ summary.hires }}</div>
            </div>
          </div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="card h-100">
            <div class="card-body">
              <div class="small text-secondary">Retiros de {{ summary.month }}</div>
              <div class="display-6 fw-semibold">{{ summary.retirements }}</div>
            </div>
          </div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="card h-100">
            <div class="card-body">
              <template v-if="summary.compare">
                <div class="small text-secondary">Frente a {{ summary.compare.label }}</div>
                <div class="display-6 fw-semibold">{{ signed(summary.compare.difference) }}</div>
                <div class="small text-secondary">
                  {{ summary.compare.active }} activos entonces<template
                    v-if="summary.compare.percent !== null"
                  >
                    · {{ signed(summary.compare.percent) }} %</template
                  >
                </div>
              </template>
              <template v-else>
                <div class="small text-secondary">Variación</div>
                <div class="text-secondary small mt-2">
                  No hay un corte anterior con qué comparar.
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-3">
        <div
          v-for="indicator in cards"
          :key="indicator.key"
          :class="WIDE_KINDS.has(indicator.kind) ? 'col-12' : 'col-12 col-lg-6'"
        >
          <IndicatorCard :indicator="indicator">
            <p v-if="indicator.kind === 'line'" class="small text-secondary mt-2 mb-0">
              Al cierre de cada año:
              <template v-for="(year, index) in indicator.data.years" :key="year.year">
                {{ index ? ' · ' : '' }}{{ year.year }}: {{ year.active }}
              </template>
            </p>
          </IndicatorCard>
        </div>
      </div>
    </div>
  </main>
</template>
