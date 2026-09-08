import BaseService from '@/shared/services/BaseService'
import type { AuthenticatedUser, LoginCredentials } from '@/types/auth.types'

export default class AuthService extends BaseService {
  private static API_URL: string = 'auth/'

  public static ensureCsrfCookie(): Promise<void> {
    return super.axiosInstance.get(`${AuthService.API_URL}csrf/`).then(() => undefined)
  }

  public static async login(credentials: LoginCredentials): Promise<AuthenticatedUser> {
    await AuthService.ensureCsrfCookie()

    const response = await super.axiosInstance.post<AuthenticatedUser>(
      `${AuthService.API_URL}login/`,
      credentials,
    )

    return response.data
  }

  public static logout(): Promise<void> {
    return super.axiosInstance.post(`${AuthService.API_URL}logout/`).then(() => undefined)
  }

  public static getCurrentUser(): Promise<AuthenticatedUser> {
    return super.axiosInstance
      .get<AuthenticatedUser>(`${AuthService.API_URL}me/`)
      .then((response) => response.data)
  }
}
