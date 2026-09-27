<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import AppHeader from '@/components/AppHeader.vue'
import EmployeeService from '@/services/EmployeeService'
import {
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
  type EmployeeFieldSpec,
} from '@/shared/employees/employeeLayout'
import BaseService from '@/shared/services/BaseService'
import { useSessionStore } from '@/stores/session'
import type { Employee, EmployeeChoices } from '@/types/employee.types'

interface DisplayRow {
  label: string
  value: string
}

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

const visibleBlocks = computed<{ title: string; rows: DisplayRow[] }[]>(() => {
  if (!employee.value) {
    return []
  }

  return EMPLOYEE_BLOCKS.map((block) => ({ title: block.title, rows: rowsOf(block) })).filter(
    (block) => block.rows.length > 0,
  )
})

const showsExtensions = computed<boolean>(() => employee.value?.extensions !== undefined)

function rowsOf(block: EmployeeBlock): DisplayRow[] {
  const current = employee.value as Employee
  const rows: DisplayRow[] = []

  for (const field of block.fields) {
    if (!(field.name in current)) {
      continue
    }

    rows.push({ label: field.label, value: formatField(current, field) })

    if (field.name === 'birth_date') {
      rows.push({ label: 'Cumpleaños', value: formatDayAndMonth(current.birth_date) })
    }

    if (field.name === 'contract_end_date') {
      rows.push({
        label: 'Vencimiento mes/año',
        value: formatMonthAndYear(current.contract_end_date),
      })
    }
  }

  return rows
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

  <main class="container py-4">
    <RouterLink class="small" :to="{ name: 'employees' }">← Volver a empleados</RouterLink>

    <div v-if="isLoading" class="text-secondary py-3" role="status">Cargando empleado…</div>

    <div v-else-if="errorMessage" class="alert alert-danger mt-3" role="alert">
      {{ errorMessage }}
    </div>

    <template v-else-if="employee">
      <div class="d-flex flex-wrap align-items-center justify-content-between gap-2 my-3">
        <div>
          <h1 class="h3 mb-0">{{ employee.full_name }}</h1>
          <p class="text-secondary mb-0">
            {{ formatChoice(choices, 'id_type', employee.id_type) }} {{ employee.id_number }}
          </p>
        </div>

        <RouterLink
          v-if="session.user?.can_edit_employees"
          class="btn btn-primary"
          :to="{ name: 'employee-edit', params: { id: employee.id } }"
        >
          Editar
        </RouterLink>
      </div>

      <section v-for="block in visibleBlocks" :key="block.title" class="card mb-3">
        <div class="card-body">
          <h2 class="h5 card-title mb-3">{{ block.title }}</h2>

          <dl class="row mb-0">
            <template v-for="row in block.rows" :key="row.label">
              <dt class="col-sm-4 col-lg-3 fw-medium">{{ row.label }}</dt>
              <dd class="col-sm-8 col-lg-9 text-break" style="white-space: pre-line">
                {{ row.value }}
              </dd>
            </template>
          </dl>
        </div>
      </section>

      <section v-if="showsExtensions" class="card mb-3">
        <div class="card-body">
          <h2 class="h5 card-title mb-3">Prórrogas de contrato</h2>

          <p v-if="!employee.extensions?.length" class="text-secondary">Sin prórrogas.</p>

          <ul v-else class="mb-3">
            <li v-for="extension in employee.extensions" :key="extension.id">
              {{ formatDate(extension.extension_date) }}
            </li>
          </ul>

          <form
            v-if="session.user?.can_edit_employees"
            class="row g-2 align-items-end"
            novalidate
            @submit.prevent="addExtension"
          >
            <div class="col-auto">
              <label class="form-label" for="extension-date">Nueva prórroga</label>
              <input
                id="extension-date"
                v-model="extensionDate"
                class="form-control"
                type="date"
                :disabled="isAddingExtension"
              />
            </div>

            <div class="col-auto">
              <button class="btn btn-outline-primary" type="submit" :disabled="isAddingExtension">
                {{ isAddingExtension ? 'Agregando…' : 'Agregar prórroga' }}
              </button>
            </div>

            <div v-if="extensionError" class="col-12">
              <div class="alert alert-danger mb-0" role="alert">{{ extensionError }}</div>
            </div>
          </form>
        </div>
      </section>
    </template>
  </main>
</template>
