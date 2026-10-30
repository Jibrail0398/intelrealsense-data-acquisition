// The Vite dev server proxies /api to the FastAPI backend (see vite.config.ts).
export const API_BASE = import.meta.env.VITE_API_BASE ?? '/api/v1'

export function wsUrl(path: string): string {
  const base = new URL(API_BASE, window.location.origin)
  base.protocol = base.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${base.toString().replace(/\/$/, '')}${path}`
}

export const streamUrl = (kind: 'rgb' | 'depth', nonce: number) =>
  `${API_BASE}/camera/stream/${kind}?n=${nonce}`

export const thumbnailUrl = (captureId: number) => `${API_BASE}/history/${captureId}/thumbnail`
