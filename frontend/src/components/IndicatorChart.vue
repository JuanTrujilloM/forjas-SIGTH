<script setup lang="ts">
import type { ChartData, ChartOptions } from 'chart.js'
import { computed, ref } from 'vue'
import { Bar, Line } from 'vue-chartjs'

import { GRID_COLOR, SERIES_COLORS } from '@/shared/charts/chartSetup'
import type { BarData, CrosstabData, LineData } from '@/types/indicator.types'

const props = defineProps<
  | { kind: 'bar'; data: BarData; title: string }
  | { kind: 'crosstab'; data: CrosstabData; title: string }
  | { kind: 'line'; data: LineData; title: string }
>()

// main code
const chart = ref<{ chart?: { toBase64Image: () => string } } | null>(null)

// past this many bars the rest folds into one; the table view still lists every one
const MAX_BARS = 15

const bars = computed<BarData | null>(() => {
  if (props.kind !== 'bar') {
    return null
  }

  const { labels, values, total } = props.data

  if (labels.length <= MAX_BARS) {
    return props.data
  }

  const rest = values.slice(MAX_BARS - 1)

  return {
    labels: [...labels.slice(0, MAX_BARS - 1), `Otros (${rest.length})`],
    values: [...values.slice(0, MAX_BARS - 1), rest.reduce((sum, value) => sum + value, 0)],
    total,
  }
})

const categoryCount = computed(() => {
  if (props.kind === 'crosstab') {
    return props.data.rows.length
  }

  return bars.value?.labels.length ?? props.data.labels.length
})

// horizontal bars grow with their categories so long labels never squeeze
const height = computed(() =>
  props.kind === 'line'
    ? 260
    : Math.max(140, categoryCount.value * (props.kind === 'crosstab' ? 40 : 28) + 64),
)

const barData = computed<ChartData<'bar'>>(() => {
  if (props.kind === 'crosstab') {
    const sexColumns = props.data.columns.slice(0, -1)

    return {
      labels: props.data.rows.map((row) => row.label),
      datasets: sexColumns.map((column, index) => ({
        label: column === 'F' ? 'Mujeres' : 'Hombres',
        data: props.data.rows.map((row) => row.values[index] ?? 0),
        backgroundColor: SERIES_COLORS[index],
        borderRadius: 4,
        borderColor: '#ffffff',
        borderWidth: 2,
        borderSkipped: 'start',
        maxBarThickness: 14,
      })),
    }
  }

  const data = bars.value ?? (props.data as BarData)

  return {
    labels: data.labels,
    datasets: [
      {
        label: props.title,
        data: data.values,
        backgroundColor: SERIES_COLORS[0],
        borderRadius: 4,
        borderSkipped: 'start',
        maxBarThickness: 16,
      },
    ],
  }
})

const barOptions = computed<ChartOptions<'bar'>>(() => ({
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: props.kind === 'crosstab', position: 'bottom', align: 'start' },
  },
  scales: {
    x: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: GRID_COLOR } },
    y: {
      grid: { display: false },
      // long names are cut on the axis; the tooltip and the table view keep them whole
      ticks: {
        callback(value) {
          const label = this.getLabelForValue(Number(value))
          return label.length > 30 ? `${label.slice(0, 29)}…` : label
        },
      },
    },
  },
}))

const lineData = computed<ChartData<'line'>>(() => {
  const data = props.data as LineData

  return {
    labels: data.labels,
    datasets: [
      {
        label: 'Activos',
        data: data.values,
        borderColor: SERIES_COLORS[0],
        backgroundColor: SERIES_COLORS[0],
        borderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
    ],
  }
})

const lineOptions: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: { legend: { display: false } },
  scales: {
    y: { ticks: { precision: 0 }, grid: { color: GRID_COLOR } },
    x: { grid: { display: false } },
  },
}

function toImage(): string | null {
  return chart.value?.chart?.toBase64Image() ?? null
}

defineExpose({ toImage })
</script>

<template>
  <div :style="{ height: `${height}px` }">
    <Line v-if="kind === 'line'" ref="chart" :data="lineData" :options="lineOptions" />
    <Bar v-else ref="chart" :data="barData" :options="barOptions" />
  </div>
</template>
