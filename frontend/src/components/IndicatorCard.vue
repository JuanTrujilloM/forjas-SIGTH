<script setup lang="ts">
import { computed, ref } from 'vue'

import IndicatorChart from '@/components/IndicatorChart.vue'
import { formatMoney } from '@/shared/employees/employeeFormat'
import type { Indicator } from '@/types/indicator.types'

const props = defineProps<{ indicator: Exclude<Indicator, { kind: 'summary' }> }>()

// main code
const chart = ref<InstanceType<typeof IndicatorChart> | null>(null)
const showsTable = ref(false)

const isChart = computed(() => ['bar', 'crosstab', 'line'].includes(props.indicator.kind))

// every chart can also be read as a table, so no value depends on color or hover alone
const table = computed<{
  columns: string[]
  rows: (string | number)[][]
  totals?: (string | number)[]
}>(() => {
  const indicator = props.indicator

  switch (indicator.kind) {
    case 'bar':
      return {
        columns: ['', 'Cantidad'],
        rows: indicator.data.labels.map((label, index) => [
          label,
          indicator.data.values[index] ?? 0,
        ]),
        totals: ['Total', indicator.data.total],
      }
    case 'crosstab':
      return {
        columns: ['', ...indicator.data.columns],
        rows: indicator.data.rows.map((row) => [row.label, ...row.values]),
        totals: ['Total', ...indicator.data.totals],
      }
    case 'line':
      return {
        columns: ['Mes', 'Activos'],
        rows: indicator.data.labels.map((label, index) => [
          label,
          indicator.data.values[index] ?? 0,
        ]),
      }
    case 'table': {
      const money = new Set(indicator.data.money_columns ?? [])
      const format = (row: (string | number)[]) =>
        row.map((value, index) => (money.has(index) ? formatMoney(String(value)) : value))

      return {
        columns: indicator.data.columns,
        rows: indicator.data.rows.map(format),
        totals: format(indicator.data.totals),
      }
    }
    default:
      return { columns: [], rows: [] }
  }
})

function isNumeric(value: string | number): boolean {
  return typeof value === 'number' || String(value).trim().startsWith('$')
}

function downloadImage(): void {
  const image = chart.value?.toImage()

  if (!image) {
    return
  }

  const link = document.createElement('a')
  link.href = image
  link.download = `${props.indicator.key}.png`
  link.click()
}
</script>

<template>
  <section class="card h-100">
    <div class="card-body d-flex flex-column">
      <div class="d-flex flex-wrap align-items-start justify-content-between gap-2 mb-2">
        <h2 class="h6 mb-0">{{ indicator.title }}</h2>

        <div v-if="isChart" class="btn-group btn-group-sm">
          <button class="btn btn-outline-secondary" type="button" @click="showsTable = !showsTable">
            {{ showsTable ? 'Ver gráfica' : 'Ver tabla' }}
          </button>
          <button
            v-if="!showsTable"
            class="btn btn-outline-secondary"
            type="button"
            :aria-label="`Descargar la gráfica ${indicator.title} como imagen`"
            @click="downloadImage"
          >
            PNG
          </button>
        </div>
      </div>

      <template v-if="indicator.kind === 'list'">
        <p v-if="!indicator.data.items.length" class="text-secondary small mb-0">
          Nadie cumple años en {{ indicator.data.month }}.
        </p>
        <ul v-else class="list-unstyled mb-0 small overflow-auto" style="max-height: 320px">
          <li
            v-for="item in indicator.data.items"
            :key="`${item.day}-${item.name}`"
            class="d-flex gap-2 py-1 border-bottom"
          >
            <span class="badge text-bg-light border fw-medium align-self-start">{{
              item.day
            }}</span>
            <span>
              {{ item.name }}
              <span class="d-block text-secondary">{{ item.detail }}</span>
            </span>
          </li>
        </ul>
      </template>

      <IndicatorChart
        v-else-if="isChart && !showsTable && indicator.kind !== 'table'"
        ref="chart"
        :kind="indicator.kind"
        :data="indicator.data as never"
        :title="indicator.title"
      />

      <div v-else class="table-responsive">
        <table class="table table-sm small mb-0">
          <thead>
            <tr>
              <th v-for="(column, index) in table.columns" :key="index" scope="col">
                {{ column }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, rowIndex) in table.rows" :key="rowIndex">
              <td
                v-for="(value, index) in row"
                :key="index"
                :class="{ 'text-end': isNumeric(value) }"
              >
                {{ value }}
              </td>
            </tr>
          </tbody>
          <tfoot v-if="table.totals">
            <tr class="fw-medium">
              <td
                v-for="(value, index) in table.totals"
                :key="index"
                :class="{ 'text-end': isNumeric(value) }"
              >
                {{ value }}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>

      <slot />
    </div>
  </section>
</template>
