import type { EmployeeField } from '@/types/employee.types'

// main code
export type EmployeeFieldKind =
  | 'text'
  | 'textarea'
  | 'email'
  | 'digits'
  | 'number'
  | 'money'
  | 'date'
  | 'choice'
  | 'boolean'
  | 'division'
  | 'section'
  | 'position'
  | 'boss'
  | 'computed'

export interface EmployeeFieldSpec {
  name: EmployeeField
  label: string
  kind: EmployeeFieldKind
  required?: boolean
  // a choice stored as a number, whose empty value is null and not ''
  nullable?: boolean
}

export type EmployeeBlockId =
  | 'identity'
  | 'contact_and_education'
  | 'employment'
  | 'compensation_and_contract'
  | 'health_and_risk'
  | 'pension_and_severance'
  | 'notes'
  | 'sociodemographic'

export interface EmployeeBlock {
  id: EmployeeBlockId
  title: string
  fields: EmployeeFieldSpec[]
}

// Same blocks as the backend's column matrix (6.2). Only the layout lives here: which of
// them a user sees is whatever the API returns.
export const EMPLOYEE_BLOCKS: EmployeeBlock[] = [
  {
    id: 'identity',
    title: 'Identidad',
    fields: [
      { name: 'status', label: 'Estado', kind: 'choice', required: true },
      { name: 'id_type', label: 'Tipo de identificación', kind: 'choice', required: true },
      { name: 'id_number', label: 'Identificación', kind: 'number', required: true },
      { name: 'full_name', label: 'Apellidos y nombres', kind: 'text', required: true },
      { name: 'birth_date', label: 'Fecha de nacimiento', kind: 'date' },
      { name: 'age', label: 'Edad', kind: 'computed' },
      { name: 'sex', label: 'Sexo', kind: 'choice' },
      { name: 'blood_type', label: 'Grupo sanguíneo', kind: 'choice' },
      { name: 'marital_status', label: 'Estado civil', kind: 'choice' },
    ],
  },
  {
    id: 'contact_and_education',
    title: 'Contacto y educación',
    fields: [
      { name: 'has_children', label: 'Tiene hijos', kind: 'boolean' },
      { name: 'mobile_phone', label: 'Celular', kind: 'digits' },
      { name: 'personal_email', label: 'Correo electrónico', kind: 'email' },
      { name: 'address', label: 'Dirección de residencia', kind: 'text' },
      { name: 'neighborhood', label: 'Barrio', kind: 'text' },
      { name: 'city', label: 'Ciudad', kind: 'text' },
      { name: 'education_level', label: 'Nivel educativo', kind: 'choice' },
      { name: 'degree_title', label: 'Título', kind: 'text' },
    ],
  },
  {
    id: 'employment',
    title: 'Laboral',
    fields: [
      { name: 'employment_type', label: 'Tipo de vinculación', kind: 'choice' },
      { name: 'category', label: 'Categoría', kind: 'choice' },
      { name: 'division', label: 'Dirección', kind: 'division' },
      { name: 'evaluation_group', label: 'Grupo de evaluación', kind: 'choice' },
      { name: 'collective_agreement', label: 'Pacto colectivo', kind: 'boolean' },
      { name: 'position', label: 'Cargo actual', kind: 'position' },
      { name: 'position_start_date', label: 'Inicio del cargo actual', kind: 'date' },
      { name: 'previous_position', label: 'Cargo anterior', kind: 'position' },
      { name: 'previous_position_start_date', label: 'Inicio del cargo anterior', kind: 'date' },
      { name: 'previous_position_end_date', label: 'Fin del cargo anterior', kind: 'date' },
      { name: 'is_leader', label: 'Es líder', kind: 'boolean' },
      { name: 'section', label: 'Sección', kind: 'section' },
      { name: 'cost_center', label: 'Centro de costos', kind: 'choice' },
      { name: 'area', label: 'Área', kind: 'choice' },
      { name: 'additional_role', label: 'Rol adicional', kind: 'choice' },
      { name: 'immediate_boss', label: 'Jefe inmediato', kind: 'boss' },
      { name: 'hire_date', label: 'Fecha de ingreso', kind: 'date' },
      { name: 'seniority', label: 'Antigüedad', kind: 'computed' },
    ],
  },
  {
    id: 'compensation_and_contract',
    title: 'Salario y contrato',
    fields: [
      { name: 'current_salary', label: 'Salario actual', kind: 'money' },
      { name: 'salary_type', label: 'Tipo de salario', kind: 'choice' },
      { name: 'hourly_rate', label: 'Valor hora', kind: 'computed' },
      { name: 'transport_allowance', label: 'Auxilio de transporte', kind: 'money' },
      { name: 'contract_type', label: 'Tipo de contrato', kind: 'choice' },
      { name: 'contract_end_date', label: 'Fecha de vencimiento', kind: 'date' },
      { name: 'indefinite_extension', label: 'Prórroga indefinido', kind: 'text' },
    ],
  },
  {
    id: 'health_and_risk',
    title: 'Salud y riesgos',
    fields: [
      { name: 'occupational_risk_insurer', label: 'ARL', kind: 'choice' },
      { name: 'health_insurer', label: 'EPS', kind: 'choice' },
    ],
  },
  {
    id: 'pension_and_severance',
    title: 'Pensión y cesantías',
    fields: [
      { name: 'pension_fund', label: 'Fondo de pensión', kind: 'choice' },
      { name: 'severance_fund', label: 'Fondo de cesantías', kind: 'choice' },
    ],
  },
  {
    id: 'notes',
    title: 'Observaciones',
    fields: [{ name: 'notes', label: 'Alertas / Observaciones', kind: 'textarea' }],
  },
  {
    id: 'sociodemographic',
    title: 'Sociodemográfico',
    fields: [
      { name: 'birth_municipality', label: 'Municipio de nacimiento', kind: 'text' },
      { name: 'nationality', label: 'Nacionalidad', kind: 'text' },
      { name: 'ethnicity', label: 'Pertenencia étnica', kind: 'choice' },
      { name: 'family_composition', label: 'Composición familiar', kind: 'choice' },
      { name: 'dependents_count', label: 'Personas a cargo', kind: 'number' },
      {
        name: 'socioeconomic_stratum',
        label: 'Estrato socioeconómico',
        kind: 'choice',
        nullable: true,
      },
    ],
  },
]
