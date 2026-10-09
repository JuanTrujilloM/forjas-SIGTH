import BaseService from '@/shared/services/BaseService'
import type { IndicatorParams, IndicatorResponse } from '@/types/indicator.types'

export default class IndicatorService extends BaseService {
  private static API_URL: string = 'indicators/'

  public static get(params: IndicatorParams): Promise<IndicatorResponse> {
    return super.axiosInstance
      .get<IndicatorResponse>(IndicatorService.API_URL, { params })
      .then((response) => response.data)
  }

  public static downloadExcel(params: IndicatorParams): Promise<void> {
    return super.downloadFile(`${IndicatorService.API_URL}export/`, params)
  }
}
