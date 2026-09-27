<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import AppHeader from '@/components/AppHeader.vue'
import EmployeeInfoCard from '@/components/EmployeeInfoCard.vue'
import EmployeePhoto from '@/components/EmployeePhoto.vue'
import EmployeeService from '@/services/EmployeeService'
import {
  daysUntil,
  formatBoolean,
  formatChoice,
  formatDate,
  formatDayAndMonth,
  formatMoney,
  formatMonthAndYear,
  formatSeniority,
} from '@/shared/employees/employeeFormat'
import {
  EMPLOYEE_BLOCKS,
  type EmployeeBlock,
  type EmployeeBlockId,
  type EmployeeFieldSpec,
} from '@/shared/employees/employeeLayout'
import BaseService from '@/shared/services/BaseService'
import { useSessionStore } from '@/stores/session'
import type {
  Employee,
  EmployeeChoices,
  EmployeeField,
  EmployeeInfoRow,
} from '@/types/employee.types'

// main code
interface StatTile {
  label: string
  value: string
  hint?: string
  tone?: 'warning' | 'danger'
}

// Shown once, in the summary or the figures on top, so the cards below do not repeat them
const SUMMARIZED_FIELDS = new Set<EmployeeField>([
  'status',
  'id_type',
  'id_number',
  'full_name',
  'photo',
  'age',
  'seniority',
  'position',
  'division',
  'section',
  'current_salary',
  'hourly_rate',
  'transport_allowance',
  'contract_end_date',
  'notes',
])

const CARD_ORDER: EmployeeBlockId[] = [
  'employment',
  'compensation_and_contract',
  'identity',
  'contact_and_education',
  'health_and_risk',
  'pension_and_severance',
  'sociodemographic',
]

const WIDE_CARDS = new Set<EmployeeBlockId>(['employment'])

const CONTRACT_WARNING_DAYS = 60

const RECENT_EXTENSIONS = 6

const route = useRoute()
const session = useSessionStore()

const employeeId = Number(route.params.id)

const employee = ref<Employee | null>(null)
const choices = ref<EmployeeChoices>({})
const isLoading = ref(false)
const errorMessage = ref<string | null>(null)

const extensionDate = ref('')
const isAddingExtension = ref(false)
const extensionError = ref<string | null>(null)
const showsAllExtensions = ref(false)

const canEdit = computed<boolean>(() => Boolean(session.user?.can_edit_employees))

const subtitle = computed<string>(() => {
  const current = employee.value

  if (!current) {
    return ''
  }

  return [current.position_name, current.division_name, current.section_name]
    .filter((part) => part)
    .join(' · ')
})

const summaryPills = computed<string[]>(() => {
  const current = employee.value

  if (!current) {
    return []
  }

  const pills: string[] = []

  if (current.age !== undefined && current.age !== null) {
    pills.push(`${current.age} años`)
  }

  if (current.seniority) {
    pills.push(`${formatSeniority(current.seniority)} en la empresa`)
  }

  if (current.immediate_boss_name) {
    pills.push(`Jefe: ${current.immediate_boss_name}`)
  }

  return pills
})

const statTiles = computed<StatTile[]>(() => {
  const current = employee.value

  if (!current) {
    return []
  }

  const tiles: StatTile[] = []

  if ('current_salary' in current) {
    tiles.push({
      label: 'Salario actual',
      value: formatMoney(current.current_salary),
      hint: formatChoice(choices.value, 'salary_type', current.salary_type),
    })
  }

  if ('hourly_rate' in current) {
    tiles.push({ label: 'Valor hora', value: formatMoney(current.hourly_rate) })
  }

  if ('transport_allowance' in current) {
    tiles.push({ label: 'Auxilio de transporte', value: formatMoney(current.transport_allowance) })
  }

  if ('contract_end_date' in current) {
    tiles.push(contractTile(current))
  }

  return tiles
})

// the contract card also holds the extensions, so it stays even with no rows of its own
const showsCompensation = computed<boolean>(
  () => employee.value !== null && 'extensions' in employee.value,
)

const cards = computed(() => {
  const current = employee.value

  if (!current) {
    return []
  }

  return CARD_ORDER.map((id) => EMPLOYEE_BLOCKS.find((block) => block.id === id) as EmployeeBlock)
    .map((block) => ({ id: block.id, title: block.title, rows: rowsOf(current, block) }))
    .filter((card) =>
      card.id === 'compensation_and_contract' ? showsCompensation.value : card.rows.length > 0,
    )
})

const hasNotes = computed<boolean>(() => Boolean(employee.value?.notes?.trim()))

const sortedExtensions = computed(() =>
  [...(employee.value?.extensions ?? [])].sort((a, b) =>
    b.extension_date.localeCompare(a.extension_date),
  ),
)

const visibleExtensions = computed(() =>
  showsAllExtensions.value
    ? sortedExtensions.value
    : sortedExtensions.value.slice(0, RECENT_EXTENSIONS),
)

function contractTile(current: Employee): StatTile {
  const days = daysUntil(current.contract_end_date)
  const tile: StatTile = {
    label: 'Vencimiento del contrato',
    value: current.contract_end_date
      ? formatMonthAndYear(current.contract_end_date)
      : current.contract_type === 'indefinite'
        ? 'Indefinido'
        : 'Sin fecha',
    hint: current.contract_end_date ? formatDate(current.contract_end_date) : undefined,
  }

  if (days === null || current.status !== 'active') {
    return tile
  }

  if (days < 0) {
    return { ...tile, hint: `Venció hace ${-days} días · ${tile.hint}`, tone: 'danger' }
  }

  if (days <= CONTRACT_WARNING_DAYS) {
    return { ...tile, hint: `Vence en ${days} días · ${tile.hint}`, tone: 'warning' }
  }

  return tile
}

function rowsOf(current: Employee, block: EmployeeBlock): EmployeeInfoRow[] {
  const rows: EmployeeInfoRow[] = []

  for (const field of block.fields) {
    if (!(field.name in current) || SUMMARIZED_FIELDS.has(field.name)) {
      continue
    }

    rows.push(row(field.label, formatField(current, field)))

    if (field.name === 'birth_date') {
      rows.push(row('Cumpleaños', formatDayAndMonth(current.birth_date)))
    }
  }

  return rows
}

function row(label: string, value: string): EmployeeInfoRow {
  return { label, value, isEmpty: value === '—' }
}

function formatField(current: Employee, field: EmployeeFieldSpec): string {
  switch (field.kind) {
    case 'date':
      return formatDate(current[field.name] as string | null)
    case 'money':
      return formatMoney(current[field.name] as string | null)
    case 'boolean':
      return formatBoolean(current[field.name] as boolean | null)
    case 'choice':
      return formatChoice(choices.value, field.name, current[field.name] as string | number | null)
    case 'position':
      return current.previous_position_name ?? '—'
    case 'boss':
      return current.immediate_boss_name ?? '—'
    default: {
      const value = current[field.name]
      return value === null || value === undefined || value === '' ? '—' : String(value)
    }
  }
}

async function loadEmployee(): Promise<void> {
  isLoading.value = true
  errorMessage.value = null

  try {
    ;[employee.value, choices.value] = await Promise.all([
      EmployeeService.get(employeeId),
      EmployeeService.getChoices(),
    ])
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudo cargar el empleado.')
  } finally {
    isLoading.value = false
  }
}

async function addExtension(): Promise<void> {
  if (!extensionDate.value) {
    extensionError.value = 'Elige la fecha de la prórroga.'
    return
  }

  isAddingExtension.value = true
  extensionError.value = null

  try {
    const extension = await EmployeeService.addExtension(employeeId, extensionDate.value)
    employee.value?.extensions?.push(extension)
    extensionDate.value = ''
  } catch (error) {
    extensionError.value = BaseService.getApiErrorMessage(error, 'No se pudo agregar la prórroga.')
  } finally {
    isAddingExtension.value = false
  }
}

onMounted(loadEmployee)
</script>

<template>
  <AppHeader />

  <main class="employee-page">
    <div class="container py-4">
      <RouterLink class="small" :to="{ name: 'employees' }">← Volver a empleados</RouterLink>

      <div v-if="isLoading" class="text-secondary py-3" role="status">Cargando empleado…</div>

      <div v-else-if="errorMessage" class="alert alert-danger mt-3" role="alert">
        {{ errorMessage }}
      </div>

      <template v-else-if="employee">
        <section class="card border-0 shadow-sm mt-3">
          <div class="card-body d-flex flex-column flex-md-row gap-4">
            <EmployeePhoto
              v-if="'photo' in employee"
              :photo-url="employee.photo ?? null"
              :employee-id="employee.id"
              :full-name="employee.full_name ?? ''"
              :can-edit="canEdit"
              @update:photo-url="employee.photo = $event"
            />

            <div class="flex-grow-1">
              <div class="d-flex flex-wrap align-items-start justify-content-between gap-2">
                <div>
                  <div class="d-flex flex-wrap align-items-center gap-2 mb-1">
                    <h1 class="h3 mb-0">{{ employee.full_name }}</h1>
                    <span
                      v-if="employee.status"
                      class="badge rounded-pill"
                      :class="
                        employee.status === 'active' ? 'text-bg-success' : 'text-bg-secondary'
                      "
                    >
                      {{ formatChoice(choices, 'status', employee.status) }}
                    </span>
                  </div>

                  <p class="text-secondary mb-0">
                    {{ formatChoice(choices, 'id_type', employee.id_type) }}
                    {{ employee.id_number }}
                  </p>
                </div>

                <RouterLink
                  v-if="canEdit"
                  class="btn btn-primary"
                  :to="{ name: 'employee-edit', params: { id: employee.id } }"
                >
                  Editar
                </RouterLink>
              </div>

              <p v-if="subtitle" class="fs-5 mt-3 mb-2">{{ subtitle }}</p>

              <ul v-if="summaryPills.length" class="list-inline mb-0">
                <li
                  v-for="pill in summaryPills"
                  :key="pill"
                  class="list-inline-item badge rounded-pill text-bg-light border fw-normal fs-6 mb-1"
                >
                  {{ pill }}
                </li>
              </ul>
            </div>
          </div>
        </section>

        <div v-if="hasNotes" class="alert alert-warning mt-3 mb-0 d-flex gap-2" role="note">
          <strong class="text-nowrap">Alertas / Observaciones:</strong>
          <span class="text-break">{{ employee.notes }}</span>
        </div>

        <div v-if="statTiles.length" class="row row-cols-2 row-cols-lg-4 g-3 mt-0">
          <div v-for="tile in statTiles" :key="tile.label" class="col">
            <div
              class="card border-0 shadow-sm h-100 stat-tile"
              :class="tile.tone ? `stat-tile--${tile.tone}` : ''"
            >
              <div class="card-body">
                <div class="small text-secondary">{{ tile.label }}</div>
                <div class="fs-4 fw-semibold text-primary text-break">{{ tile.value }}</div>
                <div
                  v-if="tile.hint"
                  class="small"
                  :class="tile.tone ? `text-${tile.tone}-emphasis fw-medium` : 'text-secondary'"
                >
                  {{ tile.hint }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="row g-3 mt-0">
          <div
            v-for="card in cards"
            :key="card.id"
            :class="WIDE_CARDS.has(card.id) ? 'col-12' : 'col-12 col-xl-6'"
          >
            <EmployeeInfoCard :title="card.title" :rows="card.rows" :wide="WIDE_CARDS.has(card.id)">
              <div v-if="card.id === 'compensation_and_contract'" class="mt-4">
                <h3 class="small text-secondary fw-normal mb-2">
                  Prórrogas de contrato ({{ sortedExtensions.length }})
                </h3>

                <p v-if="!sortedExtensions.length" class="text-body-tertiary mb-0">
                  Sin prórrogas.
                </p>

                <ol v-else class="list-unstyled d-flex flex-wrap gap-2 mb-0">
                  <li
                    v-for="(extension, index) in visibleExtensions"
                    :key="extension.id"
                    class="badge rounded-pill fw-normal"
                    :class="index === 0 ? 'text-bg-primary' : 'text-bg-light border'"
                  >
                    {{ formatDate(extension.extension_date) }}
                  </li>
                </ol>

                <button
                  v-if="sortedExtensions.length > RECENT_EXTENSIONS"
                  class="btn btn-link btn-sm px-0 mt-1"
                  type="button"
                  @click="showsAllExtensions = !showsAllExtensions"
                >
                  {{
                    showsAllExtensions
                      ? 'Ver solo las más recientes'
                      : `Ver las ${sortedExtensions.length - RECENT_EXTENSIONS} anteriores`
                  }}
                </button>

                <form
                  v-if="canEdit"
                  class="d-flex flex-wrap gap-2 align-items-end mt-3"
                  novalidate
                  @submit.prevent="addExtension"
                >
                  <div>
                    <label class="form-label small mb-1" for="extension-date">
                      Nueva prórroga
                    </label>
                    <input
                      id="extension-date"
                      v-model="extensionDate"
                      class="form-control form-control-sm"
                      type="date"
                      :disabled="isAddingExtension"
                    />
                  </div>

                  <button
                    class="btn btn-outline-primary btn-sm"
                    type="submit"
                    :disabled="isAddingExtension"
                  >
                    {{ isAddingExtension ? 'Agregando…' : 'Agregar' }}
                  </button>

                  <div v-if="extensionError" class="alert alert-danger py-1 px-2 mb-0 small w-100">
                    {{ extensionError }}
                  </div>
                </form>
              </div>
            </EmployeeInfoCard>
          </div>
        </div>
      </template>
    </div>
  </main>
</template>

<style scoped>
.employee-page {
  background: var(--fb-surface);
  min-height: 100vh;
}

.stat-tile {
  border-top: 3px solid var(--fb-blue) !important;
}

.stat-tile--warning {
  border-top-color: var(--fb-orange) !important;
}

.stat-tile--danger {
  border-top-color: var(--bs-danger) !important;
}
</style>
