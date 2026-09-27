import BaseService from '@/shared/services/BaseService'
import type {
  ContractExtension,
  Employee,
  EmployeeChoices,
  EmployeeListItem,
  EmployeeListParams,
  EmployeePayload,
  EmployeePhotoResponse,
  Page,
} from '@/types/employee.types'
import type { CatalogItem } from '@/types/organization.types'

export default class EmployeeService extends BaseService {
  private static API_URL: string = 'employees/'

  private static POSITIONS_URL: string = 'positions/'

  public static list(params: EmployeeListParams = {}): Promise<Page<EmployeeListItem>> {
    return super.axiosInstance
      .get<Page<EmployeeListItem>>(EmployeeService.API_URL, { params })
      .then((response) => response.data)
  }

  public static get(id: number): Promise<Employee> {
    return super.axiosInstance
      .get<Employee>(`${EmployeeService.API_URL}${id}/`)
      .then((response) => response.data)
  }

  public static create(payload: EmployeePayload): Promise<Employee> {
    return super.axiosInstance
      .post<Employee>(EmployeeService.API_URL, payload)
      .then((response) => response.data)
  }

  public static update(id: number, payload: EmployeePayload): Promise<Employee> {
    return super.axiosInstance
      .patch<Employee>(`${EmployeeService.API_URL}${id}/`, payload)
      .then((response) => response.data)
  }

  public static addExtension(id: number, extensionDate: string): Promise<ContractExtension> {
    return super.axiosInstance
      .post<ContractExtension>(`${EmployeeService.API_URL}${id}/extensions/`, {
        extension_date: extensionDate,
      })
      .then((response) => response.data)
  }

  public static uploadPhoto(id: number, photo: File): Promise<string> {
    const body = new FormData()
    body.append('photo', photo)

    return super.axiosInstance
      .put<EmployeePhotoResponse>(`${EmployeeService.API_URL}${id}/photo/`, body)
      .then((response) => response.data.photo)
  }

  public static removePhoto(id: number): Promise<void> {
    return super.axiosInstance
      .delete(`${EmployeeService.API_URL}${id}/photo/`)
      .then(() => undefined)
  }

  public static getChoices(): Promise<EmployeeChoices> {
    return super.axiosInstance
      .get<EmployeeChoices>(`${EmployeeService.API_URL}choices/`)
      .then((response) => response.data)
  }

  public static getPositions(): Promise<CatalogItem[]> {
    return super.axiosInstance
      .get<CatalogItem[]>(EmployeeService.POSITIONS_URL)
      .then((response) => response.data)
  }
}
