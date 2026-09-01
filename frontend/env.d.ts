/// <reference types="vite/client" />

// typed env vars so import.meta.env is not `any` under strict mode (7.10)
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
