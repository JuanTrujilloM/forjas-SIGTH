export interface IndicatorPeriod {
  value: string
  label: string
  on?: string
}

export interface SummaryData {
  active: number
  hires: number
  retirements: number
  month: string
  compare: { label: string; active: number; difference: number; percent: number | null } | null
}

export interface BarData {
  labels: string[]
  values: number[]
  total: number
}

export interface LineData {
  labels: string[]
  values: number[]
  years: { year: number; active: number }[]
}

export interface CrosstabData {
  columns: string[]
  rows: { label: string; values: number[] }[]
  totals: number[]
}

export interface TableData {
  columns: string[]
  rows: (string | number)[][]
  totals: (string | number)[]
  money_columns?: number[]
}

export interface ListData {
  month: string
  items: { name: string; day: number; detail: string }[]
}

export type Indicator =
  | { key: string; title: string; kind: 'summary'; data: SummaryData }
  | { key: string; title: string; kind: 'bar'; data: BarData }
  | { key: string; title: string; kind: 'line'; data: LineData }
  | { key: string; title: string; kind: 'crosstab'; data: CrosstabData }
  | { key: string; title: string; kind: 'table'; data: TableData }
  | { key: string; title: string; kind: 'list'; data: ListData }

export interface IndicatorResponse {
  period: IndicatorPeriod
  compare: IndicatorPeriod | null
  periods: IndicatorPeriod[]
  indicators: Indicator[]
}

export type IndicatorParams = Record<string, string | number | undefined>
