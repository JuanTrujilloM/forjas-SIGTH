import axios from 'axios'

export default class BaseService {
  public static axiosInstance = BaseService.createAxiosInstance()

  private static createAxiosInstance() {
    return axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL,
      // the session lives in Django's cookie, so it must travel on every request (10.2)
      withCredentials: true,
      xsrfCookieName: 'csrftoken',
      xsrfHeaderName: 'X-CSRFToken',
    })
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

    // DRF puts non-field errors in `detail`, already written in Spanish (4.4)
    const detail = (error.response.data as { detail?: string } | undefined)?.detail

    return detail ?? `La API respondió con estado ${error.response.status}.`
  }
}
