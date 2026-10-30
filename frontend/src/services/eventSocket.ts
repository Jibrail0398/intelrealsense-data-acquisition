import { wsUrl } from '@/constants/api'
import type { ServerEvent } from '@/types'

type Handler = (data: any) => void // eslint-disable-line @typescript-eslint/no-explicit-any

/** One WebSocket to the backend's /events, reconnecting with backoff. */
class EventSocket {
  private ws: WebSocket | null = null
  private handlers = new Map<string, Set<Handler>>()
  private retry = 0
  private timer: number | null = null
  private ping: number | null = null
  private stopped = true

  onOpenChange: ((open: boolean) => void) | null = null

  start() {
    if (!this.stopped) return
    this.stopped = false
    this.open()
  }

  stop() {
    this.stopped = true
    if (this.timer) clearTimeout(this.timer)
    if (this.ping) clearInterval(this.ping)
    this.ws?.close()
    this.ws = null
  }

  on(event: string, handler: Handler): () => void {
    if (!this.handlers.has(event)) this.handlers.set(event, new Set())
    this.handlers.get(event)!.add(handler)
    return () => this.handlers.get(event)?.delete(handler)
  }

  private open() {
    const ws = new WebSocket(wsUrl('/events'))
    this.ws = ws
    ws.onopen = () => {
      this.retry = 0
      this.onOpenChange?.(true)
      this.ping = window.setInterval(() => ws.readyState === WebSocket.OPEN && ws.send('ping'), 20_000)
    }
    ws.onmessage = (msg) => {
      const parsed = JSON.parse(msg.data) as ServerEvent
      this.handlers.get(parsed.event)?.forEach((h) => h(parsed.data))
    }
    ws.onclose = () => {
      if (this.ping) clearInterval(this.ping)
      this.onOpenChange?.(false)
      if (this.stopped) return
      const delay = Math.min(1000 * 2 ** this.retry, 10_000)
      this.retry += 1
      this.timer = window.setTimeout(() => this.open(), delay)
    }
  }
}

export const eventSocket = new EventSocket()
