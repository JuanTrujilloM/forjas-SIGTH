<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import AppHeader from '@/components/AppHeader.vue'
import EmployeePicker from '@/components/EmployeePicker.vue'
import ReportFieldPicker from '@/components/ReportFieldPicker.vue'
import ReportFilters from '@/components/ReportFilters.vue'
import ReportPreviewTable from '@/components/ReportPreviewTable.vue'
import EmployeeService from '@/services/EmployeeService'
import OrganizationService from '@/services/OrganizationService'
import ReportService from '@/services/ReportService'
import { formatChoice, formatDate } from '@/shared/employees/employeeFormat'
import { filtersFromQuery, hasActiveFilters } from '@/shared/employees/employeeListQuery'
import {
  BASE_FIELDS,
  currentMonth,
  emptyReportFilters,
  filtersToReportParams,
  MONTH_PRESETS,
  monthBounds,
  monthLabel,
  REPORT_PRESETS,
} from '@/shared/reports/reportPresets'
import BaseService from '@/shared/services/BaseService'
import type { CostCenter, EmployeeChoices } from '@/types/employee.types'
import type { CatalogItem } from '@/types/organization.types'
import type {
  ExportField,
  ReportFileFormat,
  ReportFilters as ReportFilterValues,
  ReportPage,
  ReportPreset,
} from '@/types/report.types'

const route = useRoute()

// main code
const FILE_FORMATS: { id: ReportFileFormat; label: string }[] = [
  { id: 'xlsx', label: 'Excel' },
  { id: 'csv', label: 'CSV' },
  { id: 'pdf', label: 'PDF' },
]

const DATE_LABELS: Record<string, string> = {
  hire_date: 'Ingreso',
  contract_end_date: 'Vencimiento',
  retirement_date: 'Retiro',
}

const CHOICE_LABELS: Record<string, string> = {
  status: 'Estado',
  category: 'Categoría',
  employment_type: 'Vinculación',
  contract_type: 'Contrato',
  evaluation_group: 'Grupo de evaluación',
  area: 'Área',
  sex: 'Sexo',
}

const fields = ref<ExportField[]>([])
const choices = ref<EmployeeChoices>({})
const divisions = ref<CatalogItem[]>([])
const sections = ref<CatalogItem[]>([])
const positions = ref<CatalogItem[]>([])
const costCenters = ref<CostCenter[]>([])

const preset = ref<ReportPreset>('free')
const month = ref(currentMonth())
const filters = ref<ReportFilterValues>(emptyReportFilters())
const selected = ref<string[]>([])
const leaderName = ref<string | null>(null)

const report = ref<ReportPage | null>(null)
const currentPage = ref(1)
const isLoading = ref(false)
const isReady = ref(false)
const errorMessage = ref<string | null>(null)
const downloading = ref<ReportFileFormat | null>(null)
const downloadError = ref<string | null>(null)

let previewTimer: ReturnType<typeof setTimeout> | undefined

const presetSpec = computed(
  () => REPORT_PRESETS.find((spec) => spec.id === preset.value) ?? REPORT_PRESETS[0]!,
)

const readableKeys = computed(() => new Set(fields.value.map((field) => field.key)))

const nameOf = (items: CatalogItem[], id: number | null) =>
  items.find((item) => item.id === id)?.name ?? ''

const missingRequirement = computed<string | null>(() => {
  if (preset.value === 'division' && filters.value.division === null) {
    return 'Elige la dirección del reporte.'
  }

  if (preset.value === 'section' && filters.value.section === null) {
    return 'Elige la sección del reporte.'
  }

  if (preset.value === 'leader' && filters.value.team_of === null) {
    return 'Elige el jefe cuyo equipo quieres ver.'
  }

  return selected.value.length ? null : 'Elige al menos un campo para el reporte.'
})

const title = computed<string>(() => {
  switch (preset.value) {
    case 'hires':
      return `Ingresos del mes — ${monthLabel(month.value)}`
    case 'retirements':
      return `Retiros del mes — ${monthLabel(month.value)}`
    case 'division':
      return `Empleados de ${nameOf(divisions.value, filters.value.division) || 'una dirección'}`
    case 'leader':
      return `Equipo de ${leaderName.value ?? 'un jefe'}`
    case 'section':
      return `Personal de ${nameOf(sections.value, filters.value.section) || 'una sección'}`
    default:
      return 'Reporte de empleados'
  }
})

const description = computed<string>(() => {
  const current = filters.value
  const parts: string[] = []

  if (current.search.trim()) {
    parts.push(`Búsqueda: ${current.search.trim()}`)
  }

  if (current.division !== null) {
    parts.push(`Dirección: ${nameOf(divisions.value, current.division)}`)
  }

  if (current.section !== null) {
    parts.push(`Sección: ${nameOf(sections.value, current.section)}`)
  }

  if (current.position !== null) {
    parts.push(`Cargo: ${nameOf(positions.value, current.position)}`)
  }

  if (current.cost_center !== null) {
    const center = costCenters.value.find((item) => item.id === current.cost_center)
    parts.push(`Centro de costos: ${center?.code ?? ''}`)
  }

  for (const [key, label] of Object.entries(CHOICE_LABELS)) {
    const value = current[key as keyof ReportFilterValues]
    if (value) {
      parts.push(`${label}: ${formatChoice(choices.value, key, value as string)}`)
    }
  }

  if (current.is_leader) {
    parts.push(`Es líder: ${current.is_leader === 'true' ? 'Sí' : 'No'}`)
  }

  for (const [field, label] of Object.entries(DATE_LABELS)) {
    const from = current[`${field}_from` as keyof ReportFilterValues] as string
    const to = current[`${field}_to` as keyof ReportFilterValues] as string

    if (from || to) {
      parts.push(
        `${label}: ${from ? `desde ${formatDate(from)}` : ''}${from && to ? ' ' : ''}${
          to ? `hasta ${formatDate(to)}` : ''
        }`,
      )
    }
  }

  if (current.team_of !== null) {
    parts.push(`Equipo de ${leaderName.value ?? 'un jefe'}`)
  }

  return parts.join(' · ')
})

const params = computed(() => ({
  ...filtersToReportParams(filters.value),
  fields: selected.value.join(','),
}))

function readableFields(keys: string[]): string[] {
  return keys.filter((key) => readableKeys.value.has(key))
}

function applyMonth(): void {
  const [from, to] = monthBounds(month.value)

  if (preset.value === 'hires') {
    filters.value = { ...filters.value, hire_date_from: from, hire_date_to: to }
  }

  if (preset.value === 'retirements') {
    filters.value = {
      ...filters.value,
      status: 'retired',
      retirement_date_from: from,
      retirement_date_to: to,
    }
  }
}

function applyPreset(id: ReportPreset): void {
  preset.value = id
  leaderName.value = null
  filters.value = emptyReportFilters()
  selected.value = readableFields([...BASE_FIELDS, ...presetSpec.value.extraFields])
  applyMonth()
}

function clearFilters(): void {
  applyPreset(preset.value)
}

function onLeaderSelected(id: number | null): void {
  filters.value = { ...filters.value, team_of: id }
}

async function loadPage(page: number): Promise<void> {
  currentPage.value = page

  if (missingRequirement.value) {
    report.value = null
    return
  }

  isLoading.value = true
  errorMessage.value = null

  try {
    report.value = await ReportService.getReport({ ...params.value, page })
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudo armar el reporte.')
  } finally {
    isLoading.value = false
  }
}

async function download(fileFormat: ReportFileFormat): Promise<void> {
  downloading.value = fileFormat
  downloadError.value = null

  try {
    await ReportService.download(fileFormat, {
      ...params.value,
      title: title.value,
      description: description.value,
    })
  } catch (error) {
    downloadError.value = BaseService.getApiErrorMessage(error, 'No se pudo descargar el reporte.')
  } finally {
    downloading.value = null
  }
}

watch(month, applyMonth)

watch(
  params,
  () => {
    if (!isReady.value) {
      return
    }

    clearTimeout(previewTimer)
    previewTimer = setTimeout(() => loadPage(1), 300)
  },
  { deep: true },
)

async function load(): Promise<void> {
  isLoading.value = true

  try {
    ;[
      fields.value,
      choices.value,
      divisions.value,
      sections.value,
      positions.value,
      costCenters.value,
    ] = await Promise.all([
      ReportService.getExportFields(),
      EmployeeService.getChoices(),
      OrganizationService.getDivisions(),
      OrganizationService.getSections(),
      EmployeeService.getPositions(),
      EmployeeService.getCostCenters(),
    ])
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudo cargar los reportes.')
    isLoading.value = false
    return
  }

  applyPreset('free')

  // arriving from the employee list keeps the filters that were set there
  const listFilters = filtersFromQuery(route.query)
  if (hasActiveFilters(listFilters)) {
    filters.value = {
      ...filters.value,
      search: listFilters.search,
      status: listFilters.status,
      division: listFilters.division,
      section: listFilters.section,
      hire_date_from: listFilters.hireDateFrom,
      hire_date_to: listFilters.hireDateTo,
      contract_end_date_from: listFilters.contractEndDateFrom,
      contract_end_date_to: listFilters.contractEndDateTo,
    }
  }

  isReady.value = true
  await loadPage(1)
}

onMounted(load)
</script>

<template>
  <AppHeader />

  <main class="container py-4">
    <h1 class="h3 mb-1">Reportes y consultas</h1>
    <p class="text-secondary mb-3">
      Arma un reporte con los filtros y campos que necesites, revísalo en pantalla y descárgalo.
      Solo incluye los empleados y los datos que tu perfil puede ver.
    </p>

    <div class="row g-3">
      <aside class="col-lg-4 col-xl-3 d-flex flex-column gap-3">
        <section class="card">
          <div class="card-body">
            <h2 class="h6 card-title">Reporte</h2>

            <div class="list-group list-group-flush mb-2">
              <button
                v-for="spec in REPORT_PRESETS"
                :key="spec.id"
                class="list-group-item list-group-item-action py-1 px-2 small"
                :class="{ active: preset === spec.id }"
                type="button"
                :aria-pressed="preset === spec.id"
                @click="applyPreset(spec.id)"
              >
                {{ spec.label }}
              </button>
            </div>

            <p class="small text-secondary mb-2">{{ presetSpec.description }}</p>

            <div v-if="MONTH_PRESETS.has(preset)">
              <label class="form-label small mb-1" for="report-month">Mes</label>
              <input
                id="report-month"
                v-model="month"
                class="form-control form-control-sm"
                type="month"
                required
              />
            </div>

            <div v-if="preset === 'division'">
              <label class="form-label small mb-1" for="report-preset-division">Dirección</label>
              <select
                id="report-preset-division"
                v-model="filters.division"
                class="form-select form-select-sm"
              >
                <option :value="null">Elige una dirección</option>
                <option v-for="item in divisions" :key="item.id" :value="item.id">
                  {{ item.name }}
                </option>
              </select>
            </div>

            <div v-if="preset === 'section'">
              <label class="form-label small mb-1" for="report-preset-section">Sección</label>
              <select
                id="report-preset-section"
                v-model="filters.section"
                class="form-select form-select-sm"
              >
                <option :value="null">Elige una sección</option>
                <option v-for="item in sections" :key="item.id" :value="item.id">
                  {{ item.name }}
                </option>
              </select>
            </div>

            <div v-if="preset === 'leader'">
              <label class="form-label small mb-1" for="report-leader">Jefe</label>
              <EmployeePicker
                id="report-leader"
                :model-value="filters.team_of"
                :selected-label="leaderName"
                @update:model-value="onLeaderSelected"
                @update:selected-label="leaderName = $event"
              />
            </div>
          </div>
        </section>

        <section class="card">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <h2 class="h6 card-title mb-0">Filtros</h2>
              <button class="btn btn-link btn-sm p-0" type="button" @click="clearFilters">
                Limpiar
              </button>
            </div>

            <ReportFilters
              v-model="filters"
              :choices="choices"
              :divisions="divisions"
              :sections="sections"
              :positions="positions"
              :cost-centers="costCenters"
            />
          </div>
        </section>

        <section class="card">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <h2 class="h6 card-title mb-0">Campos</h2>
              <button
                class="btn btn-link btn-sm p-0"
                type="button"
                @click="selected = readableFields([...BASE_FIELDS, ...presetSpec.extraFields])"
              >
                Restablecer
              </button>
            </div>

            <ReportFieldPicker v-model="selected" :fields="fields" />
          </div>
        </section>
      </aside>

      <section class="col-lg-8 col-xl-9">
        <div class="d-flex flex-wrap align-items-start justify-content-between gap-2 mb-2">
          <div>
            <h2 class="h5 mb-0">{{ title }}</h2>
            <p class="small text-secondary mb-0">{{ description || 'Sin filtros' }}</p>
          </div>

          <div class="btn-group" role="group" aria-label="Descargar reporte">
            <button
              v-for="option in FILE_FORMATS"
              :key="option.id"
              class="btn btn-outline-primary btn-sm"
              type="button"
              :disabled="Boolean(missingRequirement) || !report?.count || downloading !== null"
              @click="download(option.id)"
            >
              {{ downloading === option.id ? 'Generando…' : option.label }}
            </button>
          </div>
        </div>

        <div v-if="downloadError" class="alert alert-danger" role="alert">{{ downloadError }}</div>
        <div v-if="errorMessage" class="alert alert-danger" role="alert">{{ errorMessage }}</div>

        <div v-if="missingRequirement && isReady" class="alert alert-info" role="status">
          {{ missingRequirement }}
        </div>

        <div v-else-if="isLoading && !report" class="text-secondary py-3" role="status">
          Armando el reporte…
        </div>

        <ReportPreviewTable
          v-else-if="report"
          :class="{ 'opacity-50': isLoading }"
          :report="report"
          :current-page="currentPage"
          @page="loadPage"
        />
      </section>
    </div>
  </main>
</template>
