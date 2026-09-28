<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'

const MAX_BYTES = 5 * 1024 * 1024
const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp']

const props = defineProps<{
  currentUrl: string | null
  disabled?: boolean
}>()

const file = defineModel<File | null>('file', { required: true })
const remove = defineModel<boolean>('remove', { required: true })

const fileInput = ref<HTMLInputElement | null>(null)
const previewUrl = ref<string | null>(null)
const errorMessage = ref<string | null>(null)

const shownUrl = computed<string | null>(() => {
  if (previewUrl.value) {
    return previewUrl.value
  }

  return remove.value ? null : props.currentUrl
})

watch(file, (selected) => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }

  previewUrl.value = selected ? URL.createObjectURL(selected) : null
})

onBeforeUnmount(() => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
})

// Convenience before saving; the backend checks size and format again and is the one
// that decides (3.3)
function choose(event: Event): void {
  const selected = (event.target as HTMLInputElement).files?.[0]
  errorMessage.value = null

  if (!selected) {
    return
  }

  if (!ACCEPTED_TYPES.includes(selected.type)) {
    errorMessage.value = 'La foto debe ser JPG, PNG o WebP.'
  } else if (selected.size > MAX_BYTES) {
    errorMessage.value = 'La foto no puede pesar más de 5 MB.'
  } else {
    file.value = selected
    remove.value = false
  }

  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

function clear(): void {
  errorMessage.value = null

  if (file.value) {
    file.value = null
    return
  }

  remove.value = true
}
</script>

<template>
  <div class="d-flex flex-column align-items-start gap-2 flex-shrink-0">
    <img
      v-if="shownUrl"
      class="rounded border object-fit-cover"
      :src="shownUrl"
      alt="Foto del empleado"
      width="120"
      height="150"
    />

    <div
      v-else
      class="rounded border bg-light d-flex align-items-center justify-content-center text-secondary small text-center px-2"
      style="width: 120px; height: 150px"
    >
      {{ remove ? 'Se quitará al guardar' : 'Sin foto' }}
    </div>

    <div class="d-flex flex-wrap gap-2">
      <label class="btn btn-outline-primary btn-sm mb-0" :class="{ disabled }">
        {{ shownUrl ? 'Cambiar foto' : 'Elegir foto' }}
        <input
          ref="fileInput"
          class="visually-hidden"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          :disabled="disabled"
          @change="choose"
        />
      </label>

      <button
        v-if="shownUrl"
        class="btn btn-outline-secondary btn-sm"
        type="button"
        :disabled="disabled"
        @click="clear"
      >
        Quitar
      </button>

      <button
        v-else-if="remove"
        class="btn btn-link btn-sm px-0"
        type="button"
        :disabled="disabled"
        @click="remove = false"
      >
        Deshacer
      </button>
    </div>

    <div class="form-text mt-0">JPG, PNG o WebP · máx. 5 MB</div>

    <div v-if="errorMessage" class="alert alert-danger py-1 px-2 mb-0 small" role="alert">
      {{ errorMessage }}
    </div>
  </div>
</template>
