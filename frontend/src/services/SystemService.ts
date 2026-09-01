import BaseService from '@/shared/services/BaseService'
import type { SystemHealth } from '@/types/system.types'

export default class SystemService extends BaseService {
  private static API_URL: string = 'health/'

  public static getHealth(): Promise<SystemHealth> {
    return super.axiosInstance
      .get<SystemHealth>(SystemService.API_URL)
      .then((response) => response.data)
  }
}
