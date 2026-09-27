<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

import AppHeader from '@/components/AppHeader.vue'
import EmployeeService from '@/services/EmployeeService'
import OrganizationService from '@/services/OrganizationService'
import { formatChoice } from '@/shared/employees/employeeFormat'
import BaseService from '@/shared/services/BaseService'
import { useSessionStore } from '@/stores/session'
import type { EmployeeChoices, EmployeeListItem, Page } from '@/types/employee.types'
import type { CatalogItem } from '@/types/organization.types'

const session = useSessionStore()

const page = ref<Page<EmployeeListItem> | null>(null)
const choices = ref<EmployeeChoices>({})
const divisions = ref<CatalogItem[]>([])
const sections = ref<CatalogItem[]>([])

const currentPage = ref(1)
const search = ref('')
const status = ref('')
const division = ref<number | null>(null)
const section = ref<number | null>(null)

const isLoading = ref(false)
const errorMessage = ref<string | null>(null)

let searchTimer: ReturnType<typeof setTimeout> | undefined

async function loadEmployees(): Promise<void> {
  isLoading.value = true
  errorMessage.value = null

  try {
    page.value = await EmployeeService.list({
      page: currentPage.value,
      search: search.value.trim() || undefined,
      status: status.value || undefined,
      division: division.value ?? undefined,
      section: section.value ?? undefined,
    })
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudo cargar la lista.')
  } finally {
    isLoading.value = false
  }
}

async function loadFilters(): Promise<void> {
  try {
    ;[choices.value, divisions.value, sections.value] = await Promise.all([
      EmployeeService.getChoices(),
      OrganizationService.getDivisions(),
      OrganizationService.getSections(),
    ])
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudieron cargar los filtros.')
  }
}

function goToPage(target: number): void {
  currentPage.value = target
  loadEmployees()
}

watch([status, division, section], () => goToPage(1))

watch(search, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => goToPage(1), 300)
})

onMounted(() => {
  loadFilters()
  loadEmployees()
})
</script>

<template>
  <AppHeader />

  <main class="container py-4">
    <div class="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3">
      <h1 class="h3 mb-0">Empleados</h1>

      <RouterLink
        v-if="session.user?.can_edit_employees"
        class="btn btn-accent"
        :to="{ name: 'employee-create' }"
      >
        Nuevo empleado
      </RouterLink>
    </div>

    <form class="row g-2 mb-3" role="search" @submit.prevent>
      <div class="col-12 col-md-4">
        <label class="visually-hidden" for="search">Buscar</label>
        <input
          id="search"
          v-model="search"
          class="form-control"
          type="search"
          placeholder="Buscar por nombre o identificación"
        />
      </div>

      <div class="col-12 col-sm-4 col-md-2">
        <label class="visually-hidden" for="status">Estado</label>
        <select id="status" v-model="status" class="form-select">
          <option value="">Todos los estados</option>
          <option v-for="option in choices.status" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </div>

      <div class="col-12 col-sm-4 col-md-3">
        <label class="visually-hidden" for="division">Dirección</label>
        <select id="division" v-model="division" class="form-select">
          <option :value="null">Todas las direcciones</option>
          <option v-for="item in divisions" :key="item.id" :value="item.id">{{ item.name }}</option>
        </select>
      </div>

      <div class="col-12 col-sm-4 col-md-3">
        <label class="visually-hidden" for="section">Sección</label>
        <select id="section" v-model="section" class="form-select">
          <option :value="null">Todas las secciones</option>
          <option v-for="item in sections" :key="item.id" :value="item.id">{{ item.name }}</option>
        </select>
      </div>
    </form>

    <div v-if="errorMessage" class="alert alert-danger" role="alert">{{ errorMessage }}</div>

    <div v-if="isLoading" class="text-secondary py-3" role="status">Cargando empleados…</div>

    <template v-else-if="page">
      <div v-if="page.count === 0" class="alert alert-secondary" role="status">
        No hay empleados que coincidan.
      </div>

      <div v-else class="table-responsive">
        <table class="table table-hover align-middle">
          <thead>
            <tr>
              <th scope="col">Apellidos y nombres</th>
              <th scope="col">Identificación</th>
              <th scope="col">Estado</th>
              <th scope="col">Dirección</th>
              <th scope="col">Sección</th>
              <th scope="col">Cargo</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="employee in page.results" :key="employee.id">
              <td>
                <RouterLink :to="{ name: 'employee-detail', params: { id: employee.id } }">
                  {{ employee.full_name }}
                </RouterLink>
              </td>
              <td>
                {{ formatChoice(choices, 'id_type', employee.id_type) }} {{ employee.id_number }}
              </td>
              <td>
                <span
                  class="badge"
                  :class="employee.status === 'active' ? 'text-bg-success' : 'text-bg-secondary'"
                >
                  {{ formatChoice(choices, 'status', employee.status) }}
                </span>
              </td>
              <td>{{ employee.division_name ?? '—' }}</td>
              <td>{{ employee.section_name ?? '—' }}</td>
              <td>{{ employee.position_name ?? '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <nav
        v-if="page.count > 0"
        class="d-flex align-items-center justify-content-between"
        aria-label="Paginación"
      >
        <span class="text-secondary small">
          {{ page.count }} {{ page.count === 1 ? 'empleado' : 'empleados' }} · página
          {{ currentPage }}
        </span>

        <div class="btn-group">
          <button
            class="btn btn-outline-primary btn-sm"
            :disabled="!page.previous"
            @click="goToPage(currentPage - 1)"
          >
            Anterior
          </button>
          <button
            class="btn btn-outline-primary btn-sm"
            :disabled="!page.next"
            @click="goToPage(currentPage + 1)"
          >
            Siguiente
          </button>
        </div>
      </nav>
    </template>
  </main>
</template>
