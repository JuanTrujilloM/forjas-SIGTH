<script setup lang="ts">
import { computed } from 'vue'

import type { ExportField } from '@/types/report.types'

const props = defineProps<{ fields: ExportField[] }>()

const selected = defineModel<string[]>({ required: true })

// main code
const labels = computed(() => new Map(props.fields.map((field) => [field.key, field.label])))

const groups = computed(() => {
  const grouped = new Map<string, ExportField[]>()

  for (const field of props.fields) {
    grouped.set(field.group_label, [...(grouped.get(field.group_label) ?? []), field])
  }

  return [...grouped.entries()].map(([label, fields]) => ({ label, fields }))
})

function toggle(key: string): void {
  selected.value = selected.value.includes(key)
    ? selected.value.filter((current) => current !== key)
    : [...selected.value, key]
}

function move(index: number, offset: number): void {
  const target = index + offset

  if (target < 0 || target >= selected.value.length) {
    return
  }

  const reordered = [...selected.value]
  ;[reordered[index], reordered[target]] = [reordered[target] ?? '', reordered[index] ?? '']
  selected.value = reordered
}
</script>

<template>
  <div>
    <p v-if="!selected.length" class="small text-secondary mb-2">Elige al menos un campo.</p>

    <ol v-else class="list-group list-group-numbered mb-3">
      <li
        v-for="(key, index) in selected"
        :key="key"
        class="list-group-item d-flex align-items-center gap-1 py-1 px-2 small"
      >
        <span class="me-auto">{{ labels.get(key) ?? key }}</span>
        <button
          class="btn btn-sm btn-link px-1 py-0"
          type="button"
          :disabled="index === 0"
          :aria-label="`Subir ${labels.get(key)}`"
          @click="move(index, -1)"
        >
          ↑
        </button>
        <button
          class="btn btn-sm btn-link px-1 py-0"
          type="button"
          :disabled="index === selected.length - 1"
          :aria-label="`Bajar ${labels.get(key)}`"
          @click="move(index, 1)"
        >
          ↓
        </button>
        <button
          class="btn btn-sm btn-link text-danger px-1 py-0"
          type="button"
          :aria-label="`Quitar ${labels.get(key)}`"
          @click="toggle(key)"
        >
          ×
        </button>
      </li>
    </ol>

    <details v-for="group in groups" :key="group.label" class="mb-1">
      <summary class="small fw-medium">{{ group.label }}</summary>
      <div class="ps-2 pt-1">
        <div v-for="field in group.fields" :key="field.key" class="form-check small">
          <input
            :id="`field-${field.key}`"
            class="form-check-input"
            type="checkbox"
            :checked="selected.includes(field.key)"
            @change="toggle(field.key)"
          />
          <label class="form-check-label" :for="`field-${field.key}`">{{ field.label }}</label>
        </div>
      </div>
    </details>
  </div>
</template>
