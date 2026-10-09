<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AppHeader from '@/components/AppHeader.vue'
import DirectoryTabs from '@/components/DirectoryTabs.vue'
import EmployeeService from '@/services/EmployeeService'
import MonthlyCutService from '@/services/MonthlyCutService'
import OrganizationService from '@/services/OrganizationService'
import { formatChoice, formatDate, formatMonthAndYear } from '@/shared/employees/employeeFormat'
import {
  emptyFilters,
  filtersFromQuery,
  filtersToParams,
  filtersToQuery,
  hasActiveFilters,
  pageFromQuery,
} from '@/shared/employees/employeeListQuery'
import BaseService from '@/shared/services/BaseService'
import { useSessionStore } from '@/stores/session'
import type { EmployeeChoices, EmployeeListItem, MonthlyCut, Page } from '@/types/employee.types'
import type { CatalogItem } from '@/types/organization.types'

const session = useSessionStore()
const route = useRoute()
const router = useRouter()

// an account with no profile gets an empty list anyway; this only says why
const hasProfile = Boolean(session.user?.profile)

const page = ref<Page<EmployeeListItem> | null>(null)
const choices = ref<EmployeeChoices>({})
const divisions = ref<CatalogItem[]>([])
const sections = ref<CatalogItem[]>([])
const cuts = ref<MonthlyCut[]>([])
const isRetaking = ref(false)

const filters = ref(filtersFromQuery(route.query))
const currentPage = ref(pageFromQuery(route.query))

const isLoading = ref(false)
const errorMessage = ref<string | null>(null)

const canFilterByContractEnd = computed(() => session.canRead('contract_end_date'))

// a cut that no longer exists in the address bar falls back to the current data
const selectedCut = computed(() => cuts.value.find((cut) => cut.cut_date === filters.value.cut))
const canRetakeCut = computed(
  () => Boolean(session.user?.can_edit_employees) && selectedCut.value?.id === cuts.value[0]?.id,
)
const isFiltered = computed(() => hasActiveFilters(filters.value))

let searchTimer: ReturnType<typeof setTimeout> | undefined
let lastSearch = filters.value.search

async function loadEmployees(): Promise<void> {
  isLoading.value = true
  errorMessage.value = null

  try {
    const params = { ...filtersToParams(filters.value), page: currentPage.value }

    page.value = selectedCut.value
      ? await MonthlyCutService.getEmployees(selectedCut.value.id, {
          page: params.page,
          search: params.search,
          status: params.status,
          division: params.division,
          section: params.section,
        })
      : await EmployeeService.list(params)
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudo cargar la lista.')
  } finally {
    isLoading.value = false
  }
}

async function loadFilters(): Promise<void> {
  try {
    ;[choices.value, divisions.value, sections.value, cuts.value] = await Promise.all([
      EmployeeService.getChoices(),
      OrganizationService.getDivisions(),
      OrganizationService.getSections(),
      MonthlyCutService.list(),
    ])
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudieron cargar los filtros.')
  }
}

function goToPage(target: number): void {
  currentPage.value = target
  router.replace({ query: filtersToQuery(filters.value, target) })
  loadEmployees()
}

function clearFilters(): void {
  filters.value = emptyFilters()
}

async function retakeCut(): Promise<void> {
  const cut = selectedCut.value

  if (!cut) {
    return
  }

  const confirmed = window.confirm(
    `¿Rehacer el corte al ${formatDate(cut.cut_date)} con los datos de hoy? ` +
      'Reemplaza lo que guardó el corte de ese mes.',
  )

  if (!confirmed) {
    return
  }

  isRetaking.value = true
  errorMessage.value = null

  try {
    await MonthlyCutService.retake(cut.id)
    await loadEmployees()
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudo rehacer el corte.')
  } finally {
    isRetaking.value = false
  }
}

watch(
  filters,
  (current) => {
    clearTimeout(searchTimer)

    if (current.search !== lastSearch) {
      lastSearch = current.search
      searchTimer = setTimeout(() => goToPage(1), 300)
      return
    }

    goToPage(1)
  },
  { deep: true },
)

// the header link to this same route clears the query without remounting the view
watch(
  () => route.query,
  (query) => {
    const current = JSON.stringify(filtersToQuery(filters.value, currentPage.value))

    if (JSON.stringify(query) !== current) {
      filters.value = filtersFromQuery(query)
    }
  },
)

onMounted(() => {
  if (!hasProfile) {
    return
  }

  // the cuts must be known before the first load, or a month in the address bar is ignored
  loadFilters().then(loadEmployees)
})
</script>

<template>
  <AppHeader />

  <main class="container py-4">
    <DirectoryTabs />

    <div class="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3">
      <h1 class="h3 mb-0">Empleados</h1>

      <div class="d-flex gap-2">
        <RouterLink
          v-if="hasProfile && !selectedCut"
          class="btn btn-outline-primary"
          :to="{ name: 'reports', query: route.query }"
        >
          Exportar
        </RouterLink>
        <RouterLink
          v-if="session.user?.can_edit_employees"
          class="btn btn-accent"
          :to="{ name: 'employee-create' }"
        >
          Nuevo empleado
        </RouterLink>
      </div>
    </div>

    <div v-if="!hasProfile" class="alert alert-secondary" role="status">
      Tu cuenta no tiene un perfil de acceso. Pídele a TI que te lo asigne.
    </div>

    <form v-else class="row g-2 mb-3" role="search" @submit.prevent>
      <div class="col-12 col-md-4">
        <label class="visually-hidden" for="search">Buscar</label>
        <input
          id="search"
          v-model="filters.search"
          class="form-control"
          type="search"
          placeholder="Buscar por nombre o identificación"
        />
      </div>

      <div class="col-12 col-sm-4 col-md-2">
        <label class="visually-hidden" for="status">Estado</label>
        <select id="status" v-model="filters.status" class="form-select">
          <option value="">Todos los estados</option>
          <option v-for="option in choices.status" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </div>

      <div class="col-12 col-sm-4 col-md-3">
        <label class="visually-hidden" for="division">Dirección</label>
        <select id="division" v-model="filters.division" class="form-select">
          <option :value="null">Todas las direcciones</option>
          <option v-for="item in divisions" :key="item.id" :value="item.id">{{ item.name }}</option>
        </select>
      </div>

      <div class="col-12 col-sm-4 col-md-3">
        <label class="visually-hidden" for="section">Sección</label>
        <select id="section" v-model="filters.section" class="form-select">
          <option :value="null">Todas las secciones</option>
          <option v-for="item in sections" :key="item.id" :value="item.id">{{ item.name }}</option>
        </select>
      </div>

      <div class="col-12 col-sm-6 col-lg-3">
        <label class="visually-hidden" for="cut">Mes</label>
        <select id="cut" v-model="filters.cut" class="form-select">
          <option value="">Datos actuales</option>
          <option v-for="cut in cuts" :key="cut.id" :value="cut.cut_date">
            Corte de {{ formatMonthAndYear(cut.cut_date) }}
          </option>
        </select>
      </div>

      <div v-if="!selectedCut" class="col-12 col-lg-4">
        <div class="input-group">
          <span class="input-group-text">Ingreso</span>
          <input
            v-model="filters.hireDateFrom"
            class="form-control"
            type="date"
            aria-label="Fecha de ingreso desde"
          />
          <input
            v-model="filters.hireDateTo"
            class="form-control"
            type="date"
            aria-label="Fecha de ingreso hasta"
          />
        </div>
      </div>

      <div v-if="canFilterByContractEnd && !selectedCut" class="col-12 col-lg-4">
        <div class="input-group">
          <span class="input-group-text">Vencimiento</span>
          <input
            v-model="filters.contractEndDateFrom"
            class="form-control"
            type="date"
            aria-label="Fecha de vencimiento del contrato desde"
          />
          <input
            v-model="filters.contractEndDateTo"
            class="form-control"
            type="date"
            aria-label="Fecha de vencimiento del contrato hasta"
          />
        </div>
      </div>

      <div v-if="isFiltered" class="col-12 col-lg-2">
        <button class="btn btn-outline-secondary w-100" type="button" @click="clearFilters">
          Limpiar filtros
        </button>
      </div>
    </form>

    <div
      v-if="selectedCut"
      class="alert alert-info d-flex flex-wrap align-items-center justify-content-between gap-2"
      role="status"
    >
      <span>
        Datos al {{ formatDate(selectedCut.cut_date) }}, tal como quedaron en el corte mensual. La
        ficha de cada empleado muestra sus datos de hoy.
      </span>
      <button
        v-if="canRetakeCut"
        class="btn btn-outline-primary btn-sm"
        type="button"
        :disabled="isRetaking"
        @click="retakeCut"
      >
        {{ isRetaking ? 'Rehaciendo…' : 'Rehacer este corte' }}
      </button>
    </div>

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
                <div class="d-flex align-items-center gap-2">
                  <img
                    v-if="employee.photo_thumbnail"
                    class="rounded border object-fit-cover flex-shrink-0"
                    :src="employee.photo_thumbnail"
                    alt=""
                    width="40"
                    height="50"
                    loading="lazy"
                  />
                  <span
                    v-else-if="'photo_thumbnail' in employee"
                    class="rounded border bg-light flex-shrink-0"
                    style="width: 40px; height: 50px"
                    aria-hidden="true"
                  ></span>

                  <RouterLink :to="{ name: 'employee-detail', params: { id: employee.id } }">
                    {{ employee.full_name }}
                  </RouterLink>
                </div>
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
