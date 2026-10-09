<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import AppHeader from '@/components/AppHeader.vue'
import DirectoryTabs from '@/components/DirectoryTabs.vue'
import EmployeeService from '@/services/EmployeeService'
import BaseService from '@/shared/services/BaseService'
import type { OrgChartEmployee } from '@/types/employee.types'

// main code
interface SectionGroup {
  name: string
  employees: OrgChartEmployee[]
}

interface DivisionGroup {
  name: string
  count: number
  sections: SectionGroup[]
}

// management and the board belong to no division
const NO_DIVISION = 'Gerencia y Junta Directiva'

const employees = ref<OrgChartEmployee[]>([])
const isLoading = ref(false)
const errorMessage = ref<string | null>(null)

const divisions = computed<DivisionGroup[]>(() => {
  const grouped = new Map<string, Map<string, OrgChartEmployee[]>>()

  for (const employee of employees.value) {
    const division = employee.division_name ?? NO_DIVISION
    const section = employee.section_name ?? 'Sin sección'
    const sections = grouped.get(division) ?? new Map<string, OrgChartEmployee[]>()

    sections.set(section, [...(sections.get(section) ?? []), employee])
    grouped.set(division, sections)
  }

  return [...grouped.entries()]
    .map(([name, sections]) => ({
      name,
      count: [...sections.values()].reduce((total, members) => total + members.length, 0),
      sections: [...sections.entries()]
        .map(([sectionName, members]) => ({ name: sectionName, employees: members }))
        .sort((a, b) => a.name.localeCompare(b.name, 'es')),
    }))
    .sort((a, b) =>
      a.name === NO_DIVISION ? -1 : b.name === NO_DIVISION ? 1 : a.name.localeCompare(b.name, 'es'),
    )
})

async function load(): Promise<void> {
  isLoading.value = true
  errorMessage.value = null

  try {
    employees.value = await EmployeeService.getOrgChart()
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudo cargar la estructura.')
  } finally {
    isLoading.value = false
  }
}

onMounted(load)
</script>

<template>
  <AppHeader />

  <main class="container py-4">
    <DirectoryTabs />

    <h1 class="h3 mb-1">Estructura por dirección</h1>
    <p class="text-secondary small mb-3">
      Empleados activos de tu alcance, agrupados por dirección y sección.
    </p>

    <div v-if="errorMessage" class="alert alert-danger" role="alert">{{ errorMessage }}</div>

    <div v-if="isLoading" class="text-secondary py-3" role="status">Cargando estructura…</div>

    <div
      v-else-if="!errorMessage && employees.length === 0"
      class="alert alert-secondary"
      role="status"
    >
      No hay empleados activos en tu alcance.
    </div>

    <section v-for="division in divisions" v-else :key="division.name" class="card mb-3">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h2 class="h5 mb-0">{{ division.name }}</h2>
        <span class="badge text-bg-primary">{{ division.count }}</span>
      </div>

      <div class="card-body">
        <div v-for="section in division.sections" :key="section.name" class="mb-3">
          <h3 class="h6 mb-2">
            {{ section.name }}
            <span class="text-secondary fw-normal">({{ section.employees.length }})</span>
          </h3>

          <ul class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-2 list-unstyled mb-0">
            <li v-for="employee in section.employees" :key="employee.id" class="col">
              <div class="border rounded px-2 py-1 h-100 lh-sm">
                <RouterLink :to="{ name: 'employee-detail', params: { id: employee.id } }">
                  {{ employee.full_name }}
                </RouterLink>
                <div class="small text-secondary">{{ employee.position_name ?? '—' }}</div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </section>
  </main>
</template>
