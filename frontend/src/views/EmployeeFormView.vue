<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AppHeader from '@/components/AppHeader.vue'
import EmployeePhotoInput from '@/components/EmployeePhotoInput.vue'
import EmployeePicker from '@/components/EmployeePicker.vue'
import EmployeeService from '@/services/EmployeeService'
import OrganizationService from '@/services/OrganizationService'
import {
  EMPLOYEE_BLOCKS,
  type EmployeeFieldKind,
  type EmployeeFieldSpec,
} from '@/shared/employees/employeeLayout'
import BaseService from '@/shared/services/BaseService'
import type { Employee, EmployeeChoices, EmployeePayload } from '@/types/employee.types'
import type { CatalogItem } from '@/types/organization.types'

type FormValue = string | number | boolean | null

const EMPTY_AS_NULL = new Set<EmployeeFieldKind>([
  'number',
  'money',
  'date',
  'boolean',
  'division',
  'section',
  'position',
  'boss',
])

const route = useRoute()
const router = useRouter()

const employeeId = route.params.id ? Number(route.params.id) : null
const isEditing = employeeId !== null

const form = ref<Record<string, FormValue>>({})
const bossName = ref<string | null>(null)
const currentPhotoUrl = ref<string | null>(null)
const photoFile = ref<File | null>(null)
const removesPhoto = ref(false)
const choices = ref<EmployeeChoices>({})
const divisions = ref<CatalogItem[]>([])
const sections = ref<CatalogItem[]>([])
const positions = ref<CatalogItem[]>([])

const isLoading = ref(false)
const isSaving = ref(false)
const errorMessage = ref<string | null>(null)
const fieldErrors = ref<Record<string, string>>({})

const editableBlocks = computed(() =>
  EMPLOYEE_BLOCKS.map((block) => ({
    id: block.id,
    title: block.title,
    fields: block.fields.filter((field) => field.kind !== 'computed'),
  })),
)

function catalogFor(field: EmployeeFieldSpec): CatalogItem[] {
  if (field.kind === 'division') {
    return divisions.value
  }

  return field.kind === 'section' ? sections.value : positions.value
}

// inactive catalog entries stay listed only when the employee already has them
function selectableItems(field: EmployeeFieldSpec): CatalogItem[] {
  return catalogFor(field).filter((item) => item.is_active || item.id === form.value[field.name])
}

function buildPayload(): EmployeePayload {
  const payload: EmployeePayload = {}

  for (const block of editableBlocks.value) {
    for (const field of block.fields) {
      const value = form.value[field.name] ?? null
      const isEmpty = value === '' || value === null
      // null and not '' for a required field, so it fails as missing and not as an invalid choice
      const emptyValue =
        field.required || EMPTY_AS_NULL.has(field.kind) || field.nullable ? null : ''

      payload[field.name] = isEmpty ? emptyValue : value
    }
  }

  return payload
}

async function load(): Promise<void> {
  isLoading.value = true
  errorMessage.value = null

  try {
    const [loadedChoices, loadedDivisions, loadedSections, loadedPositions, employee] =
      await Promise.all([
        EmployeeService.getChoices(),
        OrganizationService.getDivisions(),
        OrganizationService.getSections(),
        EmployeeService.getPositions(),
        isEditing ? EmployeeService.get(employeeId) : Promise.resolve(null),
      ])

    choices.value = loadedChoices
    divisions.value = loadedDivisions
    sections.value = loadedSections
    positions.value = loadedPositions

    form.value = employee ? valuesOf(employee) : emptyValues()
    bossName.value = employee?.immediate_boss_name ?? null
    currentPhotoUrl.value = employee?.photo ?? null
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudo cargar el formulario.')
  } finally {
    isLoading.value = false
  }
}

function valuesOf(employee: Employee): Record<string, FormValue> {
  const values: Record<string, FormValue> = {}

  for (const block of editableBlocks.value) {
    for (const field of block.fields) {
      values[field.name] = (employee[field.name] as FormValue | undefined) ?? null
    }
  }

  return values
}

// every select needs a value that matches one of its options, or it shows up blank
function emptyValues(): Record<string, FormValue> {
  const values: Record<string, FormValue> = { status: 'active' }

  for (const block of editableBlocks.value) {
    for (const field of block.fields) {
      if (!(field.name in values)) {
        values[field.name] = field.kind === 'choice' && !field.nullable ? '' : null
      }
    }
  }

  return values
}

async function save(): Promise<void> {
  isSaving.value = true
  errorMessage.value = null
  fieldErrors.value = {}

  try {
    const saved = isEditing
      ? await EmployeeService.update(employeeId, buildPayload())
      : await EmployeeService.create(buildPayload())
    const photoSaved = await savePhoto(saved.id)

    await router.push({
      name: 'employee-detail',
      params: { id: saved.id },
      query: photoSaved ? {} : { aviso: 'foto' },
    })
  } catch (error) {
    fieldErrors.value = BaseService.getApiFieldErrors(error)
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudo guardar el empleado.')
  } finally {
    isSaving.value = false
  }
}

// The photo has its own endpoint and needs the employee to exist, so it goes after the
// data. If it fails the employee is already saved: the detail page warns and retries it.
async function savePhoto(id: number): Promise<boolean> {
  try {
    if (photoFile.value) {
      await EmployeeService.uploadPhoto(id, photoFile.value)
    } else if (removesPhoto.value && currentPhotoUrl.value) {
      await EmployeeService.removePhoto(id)
    }

    return true
  } catch {
    return false
  }
}

onMounted(load)
</script>

<template>
  <AppHeader />

  <main class="container py-4">
    <RouterLink
      class="small"
      :to="
        isEditing ? { name: 'employee-detail', params: { id: employeeId } } : { name: 'employees' }
      "
    >
      ← Volver
    </RouterLink>

    <h1 class="h3 my-3">{{ isEditing ? 'Editar empleado' : 'Nuevo empleado' }}</h1>

    <div v-if="isLoading" class="text-secondary py-3" role="status">Cargando formulario…</div>

    <form v-else novalidate @submit.prevent="save">
      <div v-if="errorMessage" class="alert alert-danger" role="alert">{{ errorMessage }}</div>

      <section v-for="block in editableBlocks" :key="block.title" class="card mb-3">
        <div class="card-body">
          <h2 class="h5 card-title mb-3">{{ block.title }}</h2>

          <div class="d-flex flex-column flex-md-row gap-4">
            <EmployeePhotoInput
              v-if="block.id === 'identity'"
              v-model:file="photoFile"
              v-model:remove="removesPhoto"
              :current-url="currentPhotoUrl"
              :disabled="isSaving"
            />

            <div class="row g-3 flex-grow-1 align-content-start">
              <div
                v-for="field in block.fields"
                :key="field.name"
                :class="
                  field.kind === 'textarea' || field.kind === 'boss'
                    ? 'col-12'
                    : 'col-md-6 col-lg-4'
                "
              >
                <label class="form-label" :for="field.name">
                  {{ field.label }}<span v-if="field.required" class="text-danger"> *</span>
                </label>

                <select
                  v-if="field.kind === 'choice'"
                  :id="field.name"
                  v-model="form[field.name]"
                  class="form-select"
                  :class="{ 'is-invalid': fieldErrors[field.name] }"
                  :disabled="isSaving"
                >
                  <option :value="field.nullable ? null : ''">Sin dato</option>
                  <option
                    v-for="option in choices[field.name]"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>

                <select
                  v-else-if="field.kind === 'boolean'"
                  :id="field.name"
                  v-model="form[field.name]"
                  class="form-select"
                  :class="{ 'is-invalid': fieldErrors[field.name] }"
                  :disabled="isSaving"
                >
                  <option :value="null">Sin dato</option>
                  <option :value="true">Sí</option>
                  <option :value="false">No</option>
                </select>

                <select
                  v-else-if="
                    field.kind === 'division' ||
                    field.kind === 'section' ||
                    field.kind === 'position'
                  "
                  :id="field.name"
                  v-model="form[field.name]"
                  class="form-select"
                  :class="{ 'is-invalid': fieldErrors[field.name] }"
                  :disabled="isSaving"
                >
                  <option :value="null">Sin dato</option>
                  <option v-for="item in selectableItems(field)" :key="item.id" :value="item.id">
                    {{ item.name }}
                  </option>
                </select>

                <EmployeePicker
                  v-else-if="field.kind === 'boss'"
                  :id="field.name"
                  :model-value="(form[field.name] as number | null) ?? null"
                  :selected-label="bossName"
                  :exclude-id="employeeId ?? undefined"
                  :disabled="isSaving"
                  :invalid="Boolean(fieldErrors[field.name])"
                  @update:model-value="form[field.name] = $event"
                />

                <textarea
                  v-else-if="field.kind === 'textarea'"
                  :id="field.name"
                  v-model="form[field.name] as string"
                  class="form-control"
                  :class="{ 'is-invalid': fieldErrors[field.name] }"
                  rows="4"
                  :disabled="isSaving"
                ></textarea>

                <input
                  v-else
                  :id="field.name"
                  v-model="form[field.name] as string"
                  class="form-control"
                  :class="{ 'is-invalid': fieldErrors[field.name] }"
                  :type="
                    field.kind === 'date'
                      ? 'date'
                      : field.kind === 'email'
                        ? 'email'
                        : field.kind === 'number' || field.kind === 'money'
                          ? 'number'
                          : 'text'
                  "
                  :inputmode="field.kind === 'digits' ? 'numeric' : undefined"
                  :min="field.kind === 'number' || field.kind === 'money' ? 0 : undefined"
                  :step="field.kind === 'money' ? '0.01' : undefined"
                  :required="field.required"
                  :disabled="isSaving"
                />

                <div v-if="fieldErrors[field.name]" class="invalid-feedback d-block">
                  {{ fieldErrors[field.name] }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <p v-if="!isEditing" class="text-secondary small">
        Las prórrogas de contrato se agregan desde el detalle, después de crear al empleado.
      </p>

      <button class="btn btn-accent" type="submit" :disabled="isSaving">
        {{ isSaving ? 'Guardando…' : 'Guardar' }}
      </button>
    </form>
  </main>
</template>
