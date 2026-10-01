/// <reference types="vite/client" />

// typed env vars so import.meta.env is not `any` under strict mode
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_CORPORATE_EMAIL_DOMAIN: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
