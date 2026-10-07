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
  | 'costCenter'
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

// same blocks as the backend's column matrix; which ones a user sees comes from the API
export const EMPLOYEE_BLOCKS: EmployeeBlock[] = [
  {
    id: 'identity',
    title: 'Identidad',
    fields: [
      { name: 'status', label: 'Estado', kind: 'choice', required: true },
      { name: 'id_type', label: 'Tipo de identificación', kind: 'choice', required: true },
      { name: 'id_number', label: 'Identificación', kind: 'number', required: true },
      { name: 'full_name', label: 'Apellidos y nombres', kind: 'text', required: true },
      { name: 'birth_date', label: 'Fecha de nacimiento', kind: 'date', required: true },
      { name: 'age', label: 'Edad', kind: 'computed' },
      { name: 'sex', label: 'Sexo', kind: 'choice', required: true },
      { name: 'blood_type', label: 'Grupo sanguíneo', kind: 'choice', required: true },
      { name: 'marital_status', label: 'Estado civil', kind: 'choice', required: true },
    ],
  },
  {
    id: 'contact_and_education',
    title: 'Contacto y educación',
    fields: [
      { name: 'has_children', label: 'Tiene hijos', kind: 'boolean', required: true },
      { name: 'mobile_phone', label: 'Celular', kind: 'digits', required: true },
      { name: 'personal_email', label: 'Correo electrónico', kind: 'email' },
      { name: 'address', label: 'Dirección de residencia', kind: 'text', required: true },
      { name: 'neighborhood', label: 'Barrio', kind: 'text', required: true },
      { name: 'city', label: 'Ciudad', kind: 'text', required: true },
      { name: 'education_level', label: 'Nivel educativo', kind: 'choice', required: true },
      { name: 'degree_title', label: 'Título', kind: 'text' },
    ],
  },
  {
    id: 'employment',
    title: 'Laboral',
    fields: [
      { name: 'employment_type', label: 'Tipo de vinculación', kind: 'choice', required: true },
      { name: 'category', label: 'Categoría', kind: 'choice', required: true },
      { name: 'division', label: 'Dirección', kind: 'division' },
      { name: 'evaluation_group', label: 'Grupo de evaluación', kind: 'choice', required: true },
      { name: 'collective_agreement', label: 'Pacto colectivo', kind: 'boolean', required: true },
      { name: 'position', label: 'Cargo actual', kind: 'position', required: true },
      {
        name: 'position_start_date',
        label: 'Inicio del cargo actual',
        kind: 'date',
        required: true,
      },
      { name: 'previous_position', label: 'Cargo anterior', kind: 'position' },
      { name: 'previous_position_start_date', label: 'Inicio del cargo anterior', kind: 'date' },
      { name: 'previous_position_end_date', label: 'Fin del cargo anterior', kind: 'date' },
      { name: 'is_leader', label: 'Es líder', kind: 'boolean', required: true },
      { name: 'section', label: 'Sección', kind: 'section', required: true },
      { name: 'cost_center', label: 'Centro de costos', kind: 'costCenter', required: true },
      { name: 'area', label: 'Área', kind: 'choice', required: true },
      { name: 'additional_role', label: 'Rol adicional', kind: 'choice', required: true },
      { name: 'immediate_boss', label: 'Jefe inmediato', kind: 'boss' },
      { name: 'hire_date', label: 'Fecha de ingreso', kind: 'date', required: true },
      { name: 'seniority', label: 'Antigüedad', kind: 'computed' },
      { name: 'training', label: 'Formación', kind: 'textarea' },
    ],
  },
  {
    id: 'compensation_and_contract',
    title: 'Salario y contrato',
    fields: [
      { name: 'current_salary', label: 'Salario actual', kind: 'money', required: true },
      { name: 'salary_type', label: 'Tipo de salario', kind: 'choice', required: true },
      { name: 'hourly_rate', label: 'Valor hora', kind: 'computed' },
      { name: 'transport_allowance', label: 'Auxilio de transporte', kind: 'money' },
      { name: 'contract_type', label: 'Tipo de contrato', kind: 'choice', required: true },
      { name: 'contract_end_date', label: 'Fecha de vencimiento', kind: 'date' },
      { name: 'indefinite_extension', label: 'Prórroga indefinido', kind: 'text' },
    ],
  },
  {
    id: 'health_and_risk',
    title: 'Salud y riesgos',
    fields: [
      { name: 'occupational_risk_insurer', label: 'ARL', kind: 'choice', required: true },
      { name: 'health_insurer', label: 'EPS', kind: 'choice', required: true },
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
      {
        name: 'birth_municipality',
        label: 'Municipio de nacimiento',
        kind: 'text',
        required: true,
      },
      { name: 'nationality', label: 'Nacionalidad', kind: 'text', required: true },
      { name: 'ethnicity', label: 'Pertenencia étnica', kind: 'choice', required: true },
      { name: 'family_composition', label: 'Composición familiar', kind: 'choice', required: true },
      { name: 'dependents_count', label: 'Personas a cargo', kind: 'number', required: true },
      {
        name: 'socioeconomic_stratum',
        label: 'Estrato socioeconómico',
        kind: 'choice',
        required: true,
        nullable: true,
      },
    ],
  },
]
