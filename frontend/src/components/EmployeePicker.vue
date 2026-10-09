<script setup lang="ts">
import { ref, watch } from 'vue'

import EmployeeService from '@/services/EmployeeService'
import BaseService from '@/shared/services/BaseService'
import type { EmployeeListItem } from '@/types/employee.types'

const props = defineProps<{
  id: string
  modelValue: number | null
  selectedLabel: string | null
  excludeId?: number
  disabled?: boolean
  invalid?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number | null]
  'update:selectedLabel': [value: string | null]
}>()

const label = ref<string | null>(props.selectedLabel)
const search = ref('')
const results = ref<EmployeeListItem[]>([])
const isLoading = ref(false)
const errorMessage = ref<string | null>(null)

let searchTimer: ReturnType<typeof setTimeout> | undefined

watch(
  () => props.selectedLabel,
  (value) => {
    label.value = value
  },
)

watch(search, (term) => {
  clearTimeout(searchTimer)

  if (term.trim().length < 3) {
    results.value = []
    return
  }

  searchTimer = setTimeout(() => findEmployees(term.trim()), 300)
})

async function findEmployees(term: string): Promise<void> {
  isLoading.value = true
  errorMessage.value = null

  try {
    const page = await EmployeeService.list({ search: term })
    results.value = page.results.filter((employee) => employee.id !== props.excludeId)
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudo buscar empleados.')
  } finally {
    isLoading.value = false
  }
}

function select(employee: EmployeeListItem): void {
  label.value = employee.full_name
  search.value = ''
  results.value = []
  emit('update:modelValue', employee.id)
  emit('update:selectedLabel', employee.full_name)
}

function clear(): void {
  label.value = null
  emit('update:modelValue', null)
  emit('update:selectedLabel', null)
}
</script>

<template>
  <div>
    <div v-if="modelValue !== null" class="input-group mb-2">
      <span class="form-control bg-light">{{ label }}</span>

      <button class="btn btn-outline-secondary" type="button" :disabled="disabled" @click="clear">
        Quitar
      </button>
    </div>

    <input
      :id="id"
      v-model="search"
      class="form-control"
      :class="{ 'is-invalid': invalid }"
      type="search"
      placeholder="Busca por nombre o identificación (mínimo 3 caracteres)"
      autocomplete="off"
      :disabled="disabled"
    />

    <div v-if="isLoading" class="form-text" role="status">Buscando…</div>

    <div v-else-if="errorMessage" class="form-text text-danger" role="alert">
      {{ errorMessage }}
    </div>

    <div v-else-if="search.trim().length >= 3 && results.length === 0" class="form-text">
      Ningún empleado coincide.
    </div>

    <div v-if="results.length" class="list-group mt-1">
      <button
        v-for="employee in results"
        :key="employee.id"
        class="list-group-item list-group-item-action"
        type="button"
        @click="select(employee)"
      >
        {{ employee.full_name }}
        <span class="text-secondary small">· {{ employee.id_number }}</span>
      </button>
    </div>
  </div>
</template>
