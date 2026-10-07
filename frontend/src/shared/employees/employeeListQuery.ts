import type { LocationQuery, LocationQueryRaw } from 'vue-router'

import type { EmployeeListParams } from '@/types/employee.types'

// main code
export interface EmployeeListFilters {
  search: string
  status: string
  division: number | null
  section: number | null
  hireDateFrom: string
  hireDateTo: string
  contractEndDateFrom: string
  contractEndDateTo: string
  cut: string
}

// the address bar is user-visible, so the keys are in Spanish like the routes
const QUERY_KEYS: Record<keyof EmployeeListFilters, string> = {
  search: 'buscar',
  status: 'estado',
  division: 'direccion',
  section: 'seccion',
  hireDateFrom: 'ingreso_desde',
  hireDateTo: 'ingreso_hasta',
  contractEndDateFrom: 'vence_desde',
  contractEndDateTo: 'vence_hasta',
  cut: 'corte',
}

const NUMERIC_FILTERS = new Set<keyof EmployeeListFilters>(['division', 'section'])

export function emptyFilters(): EmployeeListFilters {
  return {
    search: '',
    status: '',
    division: null,
    section: null,
    hireDateFrom: '',
    hireDateTo: '',
    contractEndDateFrom: '',
    contractEndDateTo: '',
    cut: '',
  }
}

function firstValue(query: LocationQuery, key: string): string {
  const value = query[key]
  const first = Array.isArray(value) ? value[0] : value
  return first ?? ''
}

export function filtersFromQuery(query: LocationQuery): EmployeeListFilters {
  const filters = emptyFilters()

  for (const [name, key] of Object.entries(QUERY_KEYS) as [keyof EmployeeListFilters, string][]) {
    const value = firstValue(query, key)

    if (NUMERIC_FILTERS.has(name)) {
      const number = Number(value)
      ;(filters[name] as number | null) = value && Number.isInteger(number) ? number : null
    } else {
      ;(filters[name] as string) = value
    }
  }

  return filters
}

export function pageFromQuery(query: LocationQuery): number {
  const page = Number(firstValue(query, 'pagina'))
  return Number.isInteger(page) && page > 1 ? page : 1
}

export function filtersToQuery(filters: EmployeeListFilters, page = 1): LocationQueryRaw {
  const query: LocationQueryRaw = {}

  for (const [name, key] of Object.entries(QUERY_KEYS) as [keyof EmployeeListFilters, string][]) {
    const value = filters[name]

    if (value !== null && value !== '') {
      query[key] = String(value).trim()
    }
  }

  if (page > 1) {
    query.pagina = String(page)
  }

  return query
}

export function filtersToParams(filters: EmployeeListFilters): EmployeeListParams {
  return {
    search: filters.search.trim() || undefined,
    status: filters.status || undefined,
    division: filters.division ?? undefined,
    section: filters.section ?? undefined,
    hire_date_from: filters.hireDateFrom || undefined,
    hire_date_to: filters.hireDateTo || undefined,
    contract_end_date_from: filters.contractEndDateFrom || undefined,
    contract_end_date_to: filters.contractEndDateTo || undefined,
  }
}

export function hasActiveFilters(filters: EmployeeListFilters): boolean {
  return Object.keys(filtersToQuery(filters)).length > 0
}
