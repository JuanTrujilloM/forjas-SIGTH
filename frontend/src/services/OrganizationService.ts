import BaseService from '@/shared/services/BaseService'
import type { CatalogItem } from '@/types/organization.types'

export default class OrganizationService extends BaseService {
  private static DIVISIONS_URL: string = 'divisions/'

  private static SECTIONS_URL: string = 'sections/'

  public static getDivisions(): Promise<CatalogItem[]> {
    return super.axiosInstance
      .get<CatalogItem[]>(OrganizationService.DIVISIONS_URL)
      .then((response) => response.data)
  }

  public static getSections(): Promise<CatalogItem[]> {
    return super.axiosInstance
      .get<CatalogItem[]>(OrganizationService.SECTIONS_URL)
      .then((response) => response.data)
  }
}
