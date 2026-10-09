import type { Page } from '@/types/employee.types'

export interface ExportField {
  key: string
  label: string
  group: string
  group_label: string
}

export interface ReportColumn {
  key: string
  label: string
}

export interface ReportRow {
  id: number
  values: string[]
}

export interface ReportPage extends Page<ReportRow> {
  columns: ReportColumn[]
}

export type ReportFileFormat = 'xlsx' | 'csv' | 'pdf'

export type ReportPreset = 'free' | 'hires' | 'retirements' | 'division' | 'leader' | 'section'

export interface ReportFilters {
  search: string
  status: string
  division: number | null
  section: number | null
  position: number | null
  cost_center: number | null
  category: string
  employment_type: string
  evaluation_group: string
  contract_type: string
  area: string
  sex: string
  is_leader: '' | 'true' | 'false'
  hire_date_from: string
  hire_date_to: string
  contract_end_date_from: string
  contract_end_date_to: string
  retirement_date_from: string
  retirement_date_to: string
  team_of: number | null
}

export type ReportParams = Record<string, string | number | undefined>
