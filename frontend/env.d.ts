/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Override the API base, e.g. http://192.168.1.20:8000/api/v1 when the backend runs elsewhere. */
  readonly VITE_API_BASE?: string
  /** Where the dev server proxies /api to. Default http://127.0.0.1:8000 */
  readonly VITE_BACKEND_URL?: string
}
