import axios from 'axios'

export default class BaseService {
  public static axiosInstance = BaseService.createAxiosInstance()

  private static createAxiosInstance() {
    return axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL,
      // the session lives in Django's cookie, so it must travel on every request
      withCredentials: true,
      xsrfCookieName: 'csrftoken',
      xsrfHeaderName: 'X-CSRFToken',
      withXSRFToken: true,
    })
  }

  public static async download(url: string, params: object): Promise<void> {
    try {
      const response = await BaseService.axiosInstance.get<Blob>(url, {
        params,
        responseType: 'blob',
      })
      const disposition = String(response.headers['content-disposition'] ?? '')
      const fileName = /filename="([^"]+)"/.exec(disposition)?.[1] ?? 'descarga'
      const link = document.createElement('a')

      link.href = URL.createObjectURL(response.data)
      link.download = fileName
      link.click()
      URL.revokeObjectURL(link.href)
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.data instanceof Blob) {
        try {
          error.response.data = JSON.parse(await error.response.data.text())
        } catch {
          error.response.data = {}
        }
      }

      throw error
    }
  }

  public static getApiErrorMessage(
    error: unknown,
    fallbackMessage = 'Ocurrió un error inesperado al contactar la API.',
  ): string {
    if (!axios.isAxiosError(error)) {
      return fallbackMessage
    }

    if (!error.response) {
      return 'No hubo respuesta de la API. Verifica que el backend esté corriendo y que el origen del frontend esté en CORS_ALLOWED_ORIGINS.'
    }
    const data = error.response.data as Record<string, unknown> | undefined

    if (typeof data?.detail === 'string') {
      return data.detail
    }

    const fieldError = Object.values(data ?? {}).find(
      (value) => Array.isArray(value) && typeof value[0] === 'string',
    ) as string[] | undefined

    return fieldError?.[0] ?? `La API respondió con estado ${error.response.status}.`
  }

  public static getApiFieldErrors(error: unknown): Record<string, string> {
    if (!axios.isAxiosError(error) || error.response?.status !== 400) {
      return {}
    }

    const data = (error.response.data ?? {}) as Record<string, unknown>
    const fieldErrors: Record<string, string> = {}

    for (const [field, messages] of Object.entries(data)) {
      if (Array.isArray(messages) && typeof messages[0] === 'string') {
        fieldErrors[field] = messages[0]
      }
    }

    return fieldErrors
  }
}
