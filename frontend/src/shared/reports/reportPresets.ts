import type { ReportFilters, ReportParams, ReportPreset } from '@/types/report.types'

// main code
export const BASE_FIELDS = [
  'id_type',
  'id_number',
  'full_name',
  'division_name',
  'section_name',
  'position_name',
  'status',
]

export interface ReportPresetSpec {
  id: ReportPreset
  label: string
  description: string
  extraFields: string[]
}

export const REPORT_PRESETS: ReportPresetSpec[] = [
  {
    id: 'free',
    label: 'Constructor libre',
    description: 'Combina los filtros y los campos que necesites.',
    extraFields: [],
  },
  {
    id: 'hires',
    label: 'Ingresos del mes',
    description: 'Empleados cuya fecha de ingreso cae en el mes elegido.',
    extraFields: ['hire_date'],
  },
  {
    id: 'retirements',
    label: 'Retiros del mes',
    description: 'Empleados retirados cuya fecha de retiro cae en el mes elegido.',
    extraFields: ['retirement_date'],
  },
  {
    id: 'division',
    label: 'Empleados por dirección',
    description: 'Los empleados de una dirección, con los campos que elijas.',
    extraFields: [],
  },
  {
    id: 'leader',
    label: 'Personal por líder',
    description: 'El equipo de un jefe: quienes le reportan y, hacia abajo, los equipos de ellos.',
    extraFields: ['immediate_boss_name'],
  },
  {
    id: 'section',
    label: 'Personal por sección',
    description: 'Los empleados de una sección.',
    extraFields: [],
  },
]

export const MONTH_PRESETS = new Set<ReportPreset>(['hires', 'retirements'])

const MONTH_NAMES = [
  'enero',
  'febrero',
  'marzo',
  'abril',
  'mayo',
  'junio',
  'julio',
  'agosto',
  'septiembre',
  'octubre',
  'noviembre',
  'diciembre',
]

export function emptyReportFilters(): ReportFilters {
  return {
    search: '',
    status: '',
    division: null,
    section: null,
    position: null,
    cost_center: null,
    category: '',
    employment_type: '',
    evaluation_group: '',
    contract_type: '',
    area: '',
    sex: '',
    is_leader: '',
    hire_date_from: '',
    hire_date_to: '',
    contract_end_date_from: '',
    contract_end_date_to: '',
    retirement_date_from: '',
    retirement_date_to: '',
    team_of: null,
  }
}

export function currentMonth(): string {
  const today = new Date()
  return `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`
}

export function monthBounds(month: string): [string, string] {
  const [year, monthNumber] = month.split('-').map(Number)
  const lastDay = new Date(year ?? 0, monthNumber ?? 1, 0).getDate()

  return [`${month}-01`, `${month}-${String(lastDay).padStart(2, '0')}`]
}

export function monthLabel(month: string): string {
  const [year, monthNumber] = month.split('-').map(Number)
  return `${MONTH_NAMES[(monthNumber ?? 1) - 1]} de ${year}`
}

export function filtersToReportParams(filters: ReportFilters): ReportParams {
  const params: ReportParams = {}

  for (const [key, value] of Object.entries(filters)) {
    if (value !== null && value !== '') {
      params[key] = typeof value === 'string' ? value.trim() : value
    }
  }

  return params
}
