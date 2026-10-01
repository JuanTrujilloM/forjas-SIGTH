<script setup lang="ts">
import { ref } from 'vue'

import EmployeeService from '@/services/EmployeeService'
import BaseService from '@/shared/services/BaseService'

const MAX_BYTES = 5 * 1024 * 1024

const props = defineProps<{
  employeeId: number
  photoUrl: string | null
  fullName: string
  canEdit: boolean
}>()

const emit = defineEmits<{
  'update:photoUrl': [value: string | null]
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const isSaving = ref(false)
const errorMessage = ref<string | null>(null)

// convenience check; the backend validates size and format again
async function upload(event: Event): Promise<void> {
  const file = (event.target as HTMLInputElement).files?.[0]

  if (!file) {
    return
  }

  errorMessage.value = null

  if (file.size > MAX_BYTES) {
    errorMessage.value = 'La foto no puede pesar más de 5 MB.'
    resetInput()
    return
  }

  isSaving.value = true

  try {
    emit('update:photoUrl', await EmployeeService.uploadPhoto(props.employeeId, file))
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudo subir la foto.')
  } finally {
    isSaving.value = false
    resetInput()
  }
}

async function remove(): Promise<void> {
  isSaving.value = true
  errorMessage.value = null

  try {
    await EmployeeService.removePhoto(props.employeeId)
    emit('update:photoUrl', null)
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudo quitar la foto.')
  } finally {
    isSaving.value = false
  }
}

function resetInput(): void {
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}
</script>

<template>
  <div class="d-flex flex-column align-items-start gap-2">
    <img
      v-if="photoUrl"
      class="rounded border object-fit-cover"
      :src="photoUrl"
      :alt="`Foto de ${fullName}`"
      width="120"
      height="150"
    />

    <div
      v-else
      class="rounded border bg-light d-flex align-items-center justify-content-center text-secondary small"
      style="width: 120px; height: 150px"
    >
      Sin foto
    </div>

    <div v-if="canEdit" class="d-flex flex-wrap gap-2">
      <label class="btn btn-outline-primary btn-sm mb-0" :class="{ disabled: isSaving }">
        {{ isSaving ? 'Guardando…' : photoUrl ? 'Cambiar foto' : 'Subir foto' }}
        <input
          ref="fileInput"
          class="visually-hidden"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          :disabled="isSaving"
          @change="upload"
        />
      </label>

      <button
        v-if="photoUrl"
        class="btn btn-outline-secondary btn-sm"
        type="button"
        :disabled="isSaving"
        @click="remove"
      >
        Quitar
      </button>
    </div>

    <div v-if="isSaving" class="visually-hidden" role="status">Guardando la foto…</div>

    <div v-if="errorMessage" class="alert alert-danger py-1 px-2 mb-0 small" role="alert">
      {{ errorMessage }}
    </div>
  </div>
</template>
