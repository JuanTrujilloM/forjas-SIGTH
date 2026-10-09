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
import type { Employee, EmployeeChoices, EmployeeInfoRow } from '@/types/employee.types'

// main code
const WIDE_BLOCKS = new Set<EmployeeBlockId>([
  'identity',
  'contact_and_education',
  'employment',
  'compensation_and_contract',
])

const CONTRACT_WARNING_DAYS = 60

const RECENT_EXTENSIONS = 6

const route = useRoute()
const session = useSessionStore()

const employeeId = Number(route.params.id)

const employee = ref<Employee | null>(null)
const choices = ref<EmployeeChoices>({})
const isLoading = ref(false)
const errorMessage = ref<string | null>(null)

const photoFailed = route.query.aviso === 'foto'

const extensionDate = ref('')
const isAddingExtension = ref(false)
const extensionError = ref<string | null>(null)
const showsAllExtensions = ref(false)

const canEdit = computed<boolean>(() => Boolean(session.user?.can_edit_employees))

const cards = computed(() => {
  const current = employee.value

  if (!current) {
    return []
  }

  return EMPLOYEE_BLOCKS.map((block) => ({
    id: block.id,
    title: block.title,
    rows: rowsOf(current, block),
  })).filter((card) => card.rows.length > 0)
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

function rowsOf(current: Employee, block: EmployeeBlock): EmployeeInfoRow[] {
  const rows: EmployeeInfoRow[] = []

  for (const field of block.fields) {
    if (!(field.name in current)) {
      continue
    }

    rows.push(rowOf(current, field))

    if (field.name === 'birth_date') {
      rows.push(plainRow('Cumpleaños', formatDayAndMonth(current.birth_date)))
    }

    if (field.name === 'contract_end_date') {
      rows.push(plainRow('Vencimiento mes/año', formatMonthAndYear(current.contract_end_date)))
    }

    if (field.name === 'cost_center' && 'cost_center_name' in current) {
      rows.push(plainRow('Nombre centro de costos', current.cost_center_name ?? '—'))
    }
  }

  return rows
}

function rowOf(current: Employee, field: EmployeeFieldSpec): EmployeeInfoRow {
  const row = plainRow(field.label, formatField(current, field))

  if (field.name === 'status' && current.status) {
    return { ...row, badge: current.status === 'active' ? 'success' : 'secondary' }
  }

  if (field.name === 'contract_end_date') {
    return { ...row, ...contractWarning(current) }
  }

  if (field.kind === 'textarea') {
    return { ...row, multiline: true }
  }

  return row
}

function plainRow(label: string, value: string): EmployeeInfoRow {
  return { label, value, isEmpty: value === '—' }
}

function contractWarning(current: Employee): Pick<EmployeeInfoRow, 'hint' | 'tone'> {
  const days = daysUntil(current.contract_end_date)

  if (days === null || current.status !== 'active') {
    return {}
  }

  if (days < 0) {
    return { hint: `Venció hace ${-days} días`, tone: 'danger' }
  }

  if (days <= CONTRACT_WARNING_DAYS) {
    return { hint: `Vence en ${days} días`, tone: 'warning' }
  }

  return {}
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
    case 'division':
      return current.division_name ?? '—'
    case 'section':
      return current.section_name ?? '—'
    case 'position':
      return (
        (field.name === 'position' ? current.position_name : current.previous_position_name) ?? '—'
      )
    case 'costCenter':
      return current.cost_center_code ?? '—'
    case 'boss':
      return current.immediate_boss_name ?? '—'
    case 'computed':
      return formatComputed(current, field.name)
    default: {
      const value = current[field.name]
      return value === null || value === undefined || value === '' ? '—' : String(value)
    }
  }
}

function formatComputed(current: Employee, name: string): string {
  if (name === 'age') {
    return current.age === null || current.age === undefined ? '—' : `${current.age} años`
  }

  if (name === 'seniority') {
    return formatSeniority(current.seniority)
  }

  return formatMoney(current.hourly_rate)
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
        <div class="d-flex flex-wrap align-items-center justify-content-between gap-2 my-3">
          <h1 class="h3 mb-0">{{ employee.full_name }}</h1>

          <RouterLink
            v-if="canEdit"
            class="btn btn-primary"
            :to="{ name: 'employee-edit', params: { id: employee.id } }"
          >
            Editar
          </RouterLink>
        </div>

        <div v-if="photoFailed" class="alert alert-warning" role="alert">
          Los datos del empleado se guardaron, pero la foto no se pudo subir. Súbela de nuevo desde
          la sección Identidad.
        </div>

        <div class="row g-3">
          <div
            v-for="card in cards"
            :key="card.id"
            :class="WIDE_BLOCKS.has(card.id) ? 'col-12' : 'col-12 col-lg-6'"
          >
            <EmployeeInfoCard
              :title="card.title"
              :rows="card.rows"
              :wide="WIDE_BLOCKS.has(card.id)"
              :highlight="card.id === 'notes' && hasNotes"
            >
              <template v-if="card.id === 'identity' && 'photo' in employee" #aside>
                <EmployeePhoto
                  :photo-url="employee.photo ?? null"
                  :employee-id="employee.id"
                  :full-name="employee.full_name ?? ''"
                  :can-edit="canEdit"
                  @update:photo-url="employee.photo = $event"
                />
              </template>

              <div
                v-if="card.id === 'compensation_and_contract' && 'extensions' in employee"
                class="border-top pt-3 mt-4"
              >
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
</style>
