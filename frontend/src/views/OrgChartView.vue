<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import AppHeader from '@/components/AppHeader.vue'
import DirectoryTabs from '@/components/DirectoryTabs.vue'
import OrgChartNode from '@/components/OrgChartNode.vue'
import EmployeeService from '@/services/EmployeeService'
import BaseService from '@/shared/services/BaseService'
import type { OrgChartEmployee } from '@/types/employee.types'

// main code
const employees = ref<OrgChartEmployee[]>([])
const isLoading = ref(false)
const errorMessage = ref<string | null>(null)
const expandAll = ref<{ open: boolean; version: number } | null>(null)

const teams = computed(() => {
  const byBoss = new Map<number, OrgChartEmployee[]>()

  for (const employee of employees.value) {
    if (employee.immediate_boss !== null) {
      byBoss.set(employee.immediate_boss, [
        ...(byBoss.get(employee.immediate_boss) ?? []),
        employee,
      ])
    }
  }

  return byBoss
})

// a boss outside the user's scope (or retired) leaves the employee at the top of the tree
const roots = computed(() => {
  const visible = new Set(employees.value.map((employee) => employee.id))

  return employees.value
    .filter((employee) => employee.immediate_boss === null || !visible.has(employee.immediate_boss))
    .sort((a, b) => Number(a.immediate_boss !== null) - Number(b.immediate_boss !== null))
})

function childrenOf(id: number): OrgChartEmployee[] {
  return teams.value.get(id) ?? []
}

function setExpanded(open: boolean): void {
  expandAll.value = { open, version: (expandAll.value?.version ?? 0) + 1 }
}

async function load(): Promise<void> {
  isLoading.value = true
  errorMessage.value = null

  try {
    employees.value = await EmployeeService.getOrgChart()
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudo cargar el organigrama.')
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

    <div class="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-1">
      <h1 class="h3 mb-0">Organigrama</h1>

      <div v-if="employees.length" class="btn-group btn-group-sm">
        <button class="btn btn-outline-primary" type="button" @click="setExpanded(true)">
          Expandir todo
        </button>
        <button class="btn btn-outline-primary" type="button" @click="setExpanded(false)">
          Contraer todo
        </button>
      </div>
    </div>
    <p class="text-secondary small mb-3">
      Empleados activos de tu alcance, ordenados por jefe inmediato.
    </p>

    <div v-if="errorMessage" class="alert alert-danger" role="alert">{{ errorMessage }}</div>

    <div v-if="isLoading" class="text-secondary py-3" role="status">Cargando organigrama…</div>

    <div
      v-else-if="!errorMessage && employees.length === 0"
      class="alert alert-secondary"
      role="status"
    >
      No hay empleados activos en tu alcance.
    </div>

    <ul v-else class="list-unstyled mb-0 overflow-x-auto">
      <OrgChartNode
        v-for="employee in roots"
        :key="employee.id"
        :employee="employee"
        :children-of="childrenOf"
        :depth="0"
        is-root
        :expand-all="expandAll"
      />
    </ul>
  </main>
</template>
