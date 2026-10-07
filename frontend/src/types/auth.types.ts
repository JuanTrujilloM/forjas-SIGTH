export type AccessProfile =
  'talent_management' | 'general_management' | 'occupational_safety' | 'director' | 'leader' | ''

export interface AuthenticatedUser {
  id: number
  email: string
  first_name: string
  last_name: string
  full_name: string
  profile: AccessProfile
  profile_name: string
  division: number | null
  division_name: string | null
  section_names: string[]
  sees_every_employee: boolean
  can_edit_employees: boolean
  readable_fields: string[]
}

export interface LoginCredentials {
  email: string
  password: string
}
