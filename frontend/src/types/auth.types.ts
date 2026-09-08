export interface AuthenticatedUser {
  id: number
  email: string
  first_name: string
  last_name: string
  full_name: string
  division: number | null
  division_name: string | null
  sees_every_division: boolean
}

export interface LoginCredentials {
  email: string
  password: string
}
