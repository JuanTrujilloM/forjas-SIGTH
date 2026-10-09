import BaseService from '@/shared/services/BaseService'
import type { ExportField, ReportFileFormat, ReportPage, ReportParams } from '@/types/report.types'

export default class ReportService extends BaseService {
  private static API_URL: string = 'employees/'

  public static getExportFields(): Promise<ExportField[]> {
    return super.axiosInstance
      .get<ExportField[]>(`${ReportService.API_URL}export-fields/`)
      .then((response) => response.data)
  }

  public static getReport(params: ReportParams): Promise<ReportPage> {
    return super.axiosInstance
      .get<ReportPage>(`${ReportService.API_URL}report/`, { params })
      .then((response) => response.data)
  }

  public static download(fileFormat: ReportFileFormat, params: ReportParams): Promise<void> {
    return super.downloadFile(`${ReportService.API_URL}export/`, { ...params, file_format: fileFormat })
  }
}
