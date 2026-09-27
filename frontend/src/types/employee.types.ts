export interface Page<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ChoiceOption {
  value: string | number
  label: string
}

export type EmployeeChoices = Partial<Record<string, ChoiceOption[]>>

export interface Seniority {
  years: number
  months: number
}

export interface ContractExtension {
  id: number
  extension_date: string
}

export interface EmployeeListItem {
  id: number
  status: string
  id_type: string
  id_number: number
  full_name: string
  division_name: string | null
  section_name: string | null
  position_name: string | null
}

// Every field but the id is optional: the backend leaves out the columns the profile may
// not read (6.2), so a missing key means "not yours to see", not "empty"
export interface Employee {
  id: number
  status?: string
  id_type?: string
  id_number?: number
  full_name?: string
  birth_date?: string | null
  age?: number | null
  sex?: string
  blood_type?: string
  marital_status?: string
  has_children?: boolean | null
  mobile_phone?: string
  personal_email?: string
  address?: string
  neighborhood?: string
  city?: string
  education_level?: string
  degree_title?: string
  employment_type?: string
  category?: string
  division?: number | null
  division_name?: string | null
  evaluation_group?: string
  collective_agreement?: boolean | null
  position?: number | null
  position_name?: string | null
  position_start_date?: string | null
  previous_position?: number | null
  previous_position_name?: string | null
  previous_position_start_date?: string | null
  previous_position_end_date?: string | null
  is_leader?: boolean | null
  section?: number | null
  section_name?: string | null
  cost_center?: string
  area?: string
  additional_role?: string
  immediate_boss?: number | null
  immediate_boss_name?: string | null
  hire_date?: string | null
  seniority?: Seniority | null
  current_salary?: string | null
  salary_type?: string
  hourly_rate?: string | null
  transport_allowance?: string | null
  contract_type?: string
  contract_end_date?: string | null
  extensions?: ContractExtension[]
  indefinite_extension?: string
  occupational_risk_insurer?: string
  health_insurer?: string
  pension_fund?: string
  severance_fund?: string
  notes?: string
  birth_municipality?: string
  nationality?: string
  ethnicity?: string
  family_composition?: string
  dependents_count?: number | null
  socioeconomic_stratum?: number | null
}

export type EmployeeField = Exclude<keyof Employee, 'id'>

export type EmployeePayload = Partial<Record<EmployeeField, unknown>>

export interface EmployeeListParams {
  page?: number
  search?: string
  status?: string
  division?: number
  section?: number
}
