import axios, { AxiosError } from 'axios'

import { API_BASE } from '@/constants/api'

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number | null,
    public readonly code: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export const api = axios.create({ baseURL: API_BASE, timeout: 15_000 })

// Every backend error has the shape {"error": {"code", "message"}}.
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ error?: { code: string; message: string } }>) => {
    if (!error.response) {
      return Promise.reject(
        new ApiError('Cannot reach the backend. Is the FastAPI server running on port 8000?', null, 'offline'),
      )
    }
    const body = error.response.data?.error
    return Promise.reject(
      new ApiError(body?.message ?? error.message, error.response.status, body?.code ?? 'http_error'),
    )
  },
)

export function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : String(err)
}
