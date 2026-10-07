import BaseService from '@/shared/services/BaseService'
import type { EmployeeListItem, EmployeeListParams, MonthlyCut, Page } from '@/types/employee.types'

export default class MonthlyCutService extends BaseService {
  private static API_URL: string = 'monthly-cuts/'

  public static list(): Promise<MonthlyCut[]> {
    return super.axiosInstance
      .get<MonthlyCut[]>(MonthlyCutService.API_URL)
      .then((response) => response.data)
  }

  public static getEmployees(
    cutId: number,
    params: EmployeeListParams,
  ): Promise<Page<EmployeeListItem>> {
    return super.axiosInstance
      .get<Page<EmployeeListItem>>(`${MonthlyCutService.API_URL}${cutId}/employees/`, { params })
      .then((response) => response.data)
  }

  public static retake(cutId: number): Promise<MonthlyCut> {
    return super.axiosInstance
      .post<MonthlyCut>(`${MonthlyCutService.API_URL}${cutId}/retake/`)
      .then((response) => response.data)
  }
}
