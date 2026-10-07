import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import AuthService from '@/services/AuthService'
import type { AuthenticatedUser, LoginCredentials } from '@/types/auth.types'

// main code
export const useSessionStore = defineStore('session', () => {
  const user = ref<AuthenticatedUser | null>(null)
  const isRestored = ref(false)

  const isAuthenticated = computed<boolean>(() => user.value !== null)

  // interface convenience only: the backend drops a hidden column on its own
  function canRead(field: string): boolean {
    return user.value?.readable_fields.includes(field) ?? false
  }

  async function restore(): Promise<void> {
    try {
      user.value = await AuthService.getCurrentUser()
    } catch {
      user.value = null
    } finally {
      isRestored.value = true
    }
  }

  async function login(credentials: LoginCredentials): Promise<void> {
    user.value = await AuthService.login(credentials)
    isRestored.value = true
  }

  async function logout(): Promise<void> {
    try {
      await AuthService.logout()
    } finally {
      user.value = null
    }
  }

  return { user, isRestored, isAuthenticated, canRead, restore, login, logout }
})
