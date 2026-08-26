export class BackendError extends Error {
  constructor(
    message: string,
    public readonly kind: 'network' | 'server' | 'client' = 'network',
  ) {
    super(message)
    this.name = 'BackendError'
  }
}

const API_BASE: string = import.meta.env.VITE_API_URL ?? '/api'

export function isMockMode(): boolean {
  return !import.meta.env.VITE_API_URL
}

export async function apiRequest<T>(
  path: string,
  init?: RequestInit,
  timeoutMs = 8000,
): Promise<T> {
  if (isMockMode()) {
    throw new BackendError(
      'apiRequest must not be called in mock mode',
      'client',
    )
  }
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...(init?.headers ?? {}),
      },
    })
    if (!res.ok) {
      throw new BackendError(
        `Backend request failed: ${res.status} ${res.statusText}`,
        res.status >= 500 ? 'server' : 'client',
      )
    }
    return (await res.json()) as T
  } catch (err) {
    if (err instanceof BackendError) throw err
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new BackendError('Backend request timed out', 'network')
    }
    throw new BackendError('Unable to communicate with local backend.', 'network')
  } finally {
    clearTimeout(timer)
  }
}
