<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import AppHeader from '@/components/AppHeader.vue'
import EmployeeService from '@/services/EmployeeService'
import {
  CONTRACT_ALERT_DAYS,
  describeContractEnd,
  formatChoice,
  formatDate,
} from '@/shared/employees/employeeFormat'
import BaseService from '@/shared/services/BaseService'
import type { ContractAlert, EmployeeChoices } from '@/types/employee.types'

// main code
const alerts = ref<ContractAlert[]>([])
const choices = ref<EmployeeChoices>({})
const isLoading = ref(false)
const errorMessage = ref<string | null>(null)

const expiredCount = computed(
  () => alerts.value.filter((alert) => alert.days_until_contract_end < 0).length,
)

const summary = computed(() => {
  const count = alerts.value.length
  return `${count} ${count === 1 ? 'contrato' : 'contratos'} en alerta.`
})

const expiredSummary = computed(() =>
  expiredCount.value === 1 ? '1 ya vencido.' : `${expiredCount.value} ya vencidos.`,
)

async function load(): Promise<void> {
  isLoading.value = true
  errorMessage.value = null

  try {
    ;[alerts.value, choices.value] = await Promise.all([
      EmployeeService.getContractAlerts(),
      EmployeeService.getChoices(),
    ])
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(
      error,
      'No se pudieron cargar los vencimientos.',
    )
  } finally {
    isLoading.value = false
  }
}

onMounted(load)
</script>

<template>
  <AppHeader />

  <main class="container py-4">
    <h1 class="h3 mb-1">Vencimientos de contrato</h1>
    <p class="text-secondary mb-3">
      Empleados activos cuyo contrato vence en los próximos {{ CONTRACT_ALERT_DAYS }} días, y los
      que ya vencieron sin una prórroga registrada. La lista se recalcula cada día; un contrato sale
      de aquí al registrar su prórroga o al retirar al empleado.
    </p>

    <div v-if="errorMessage" class="alert alert-danger" role="alert">{{ errorMessage }}</div>

    <div v-if="isLoading" class="text-secondary py-3" role="status">Cargando vencimientos…</div>

    <template v-else-if="!errorMessage">
      <div v-if="alerts.length === 0" class="alert alert-success" role="status">
        Ningún contrato vence en los próximos {{ CONTRACT_ALERT_DAYS }} días.
      </div>

      <template v-else>
        <p class="small mb-2" role="status">
          {{ summary }}
          <span v-if="expiredCount" class="text-danger fw-medium">{{ expiredSummary }}</span>
        </p>

        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th scope="col">Estado</th>
                <th scope="col">Vence</th>
                <th scope="col">Apellidos y nombres</th>
                <th scope="col">Identificación</th>
                <th scope="col">Cargo</th>
                <th scope="col">Sección</th>
                <th scope="col">Contrato</th>
                <th scope="col" class="text-end">Prórrogas</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="alert in alerts"
                :key="alert.id"
                :class="{ 'table-danger': alert.days_until_contract_end < 0 }"
              >
                <td>
                  <span
                    class="badge"
                    :class="
                      alert.days_until_contract_end < 0 ? 'text-bg-danger' : 'text-bg-warning'
                    "
                  >
                    {{ describeContractEnd(alert.days_until_contract_end) }}
                  </span>
                </td>
                <td class="text-nowrap">{{ formatDate(alert.contract_end_date) }}</td>
                <td>
                  <RouterLink :to="{ name: 'employee-detail', params: { id: alert.id } }">
                    {{ alert.full_name }}
                  </RouterLink>
                </td>
                <td class="text-nowrap">
                  {{ formatChoice(choices, 'id_type', alert.id_type) }} {{ alert.id_number }}
                </td>
                <td>{{ alert.position_name ?? '—' }}</td>
                <td>{{ alert.section_name ?? '—' }}</td>
                <td>{{ formatChoice(choices, 'contract_type', alert.contract_type) }}</td>
                <td class="text-end">{{ alert.extension_count }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </template>
  </main>
</template>
