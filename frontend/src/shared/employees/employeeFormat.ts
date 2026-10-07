import type { EmployeeChoices, Seniority } from '@/types/employee.types'

// main code
const MONTHS = [
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

const moneyFormatter = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  maximumFractionDigits: 2,
})

// split by hand: new Date('YYYY-MM-DD') is UTC midnight, the previous day in Colombia
function splitDate(value: string): [number, number, number] {
  const [year, month, day] = value.split('-').map(Number)
  return [year ?? 0, month ?? 1, day ?? 1]
}

export function formatDate(value: string | null | undefined): string {
  if (!value) {
    return '—'
  }

  const [year, month, day] = splitDate(value)
  return `${String(day).padStart(2, '0')}/${MONTHS[month - 1]}/${year}`
}

export function formatDayAndMonth(value: string | null | undefined): string {
  if (!value) {
    return '—'
  }

  const [, month, day] = splitDate(value)
  return `${day} de ${MONTHS[month - 1]}`
}

export function formatMonthAndYear(value: string | null | undefined): string {
  if (!value) {
    return '—'
  }

  const [year, month] = splitDate(value)
  return `${MONTHS[month - 1]} de ${year}`
}

export function formatMoney(value: string | null | undefined): string {
  return value === null || value === undefined || value === ''
    ? '—'
    : moneyFormatter.format(Number(value))
}

export function formatBoolean(value: boolean | null | undefined): string {
  if (value === null || value === undefined) {
    return '—'
  }

  return value ? 'Sí' : 'No'
}

export function formatSeniority(value: Seniority | null | undefined): string {
  if (!value) {
    return '—'
  }

  return `${value.years} ${value.years === 1 ? 'año' : 'años'}, ${value.months} ${value.months === 1 ? 'mes' : 'meses'}`
}

export function formatChoice(
  choices: EmployeeChoices,
  field: string,
  value: string | number | null | undefined,
): string {
  if (value === null || value === undefined || value === '') {
    return '—'
  }

  return choices[field]?.find((option) => option.value === value)?.label ?? String(value)
}

export function daysUntil(value: string | null | undefined): number | null {
  if (!value) {
    return null
  }

  const [year, month, day] = splitDate(value)
  const today = new Date()
  const target = Date.UTC(year, month - 1, day)
  const start = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate())

  return Math.round((target - start) / 86_400_000)
}

// same threshold as the backend's contract alert, so the detail and the alert page agree
export const CONTRACT_ALERT_DAYS = 50

export function describeContractEnd(days: number): string {
  if (days < 0) {
    return `Vencido hace ${-days} ${days === -1 ? 'día' : 'días'}`
  }

  if (days === 0) {
    return 'Vence hoy'
  }

  return `Vence en ${days} ${days === 1 ? 'día' : 'días'}`
}
