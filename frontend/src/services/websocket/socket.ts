import { isMockMode } from '@/services/api/client'
import { mockEngine } from './mockEngine'

export type SocketEventHandler = (payload: unknown) => void

const WS_URL: string = import.meta.env.VITE_WS_URL ?? 'ws://localhost:5000/ws'

type ConnState = 'idle' | 'connecting' | 'open' | 'closed'

class SocketClient {
  private ws: WebSocket | null = null
  private handlers = new Map<string, Set<SocketEventHandler>>()
  private reconnectAttempts = 0
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private state: ConnState = 'idle'

  get connectionState(): ConnState {
    return this.state
  }

  connect() {
    if (this.state === 'open' || this.state === 'connecting') return
    if (isMockMode()) {
      mockEngine.boot()
      this.state = 'open'
      return
    }
    this.state = 'connecting'
    try {
      this.ws = new WebSocket(WS_URL)
    } catch {
      this.scheduleReconnect()
      return
    }
    this.ws.onopen = () => {
      this.state = 'open'
      this.reconnectAttempts = 0
    }
    this.ws.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data as string) as { event: string; payload?: unknown }
        if (msg.event) this.dispatch(msg.event, msg.payload ?? {})
      } catch {
        // ignore malformed frames
      }
    }
    this.ws.onclose = () => {
      this.state = 'closed'
      this.scheduleReconnect()
    }
    this.ws.onerror = () => {
      this.ws?.close()
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimer !== null) return
    const delay = Math.min(1000 * 2 ** this.reconnectAttempts, 15000)
    this.reconnectAttempts += 1
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null
      this.connect()
    }, delay)
  }

  disconnect() {
    if (this.reconnectTimer !== null) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    this.ws?.close()
    this.ws = null
    this.state = 'closed'
  }

  on(event: string, cb: SocketEventHandler): () => void {
    if (!this.handlers.has(event)) this.handlers.set(event, new Set())
    this.handlers.get(event)!.add(cb)
    const removeLocal = () => this.handlers.get(event)?.delete(cb)
    if (isMockMode()) {
      const removeMock = mockEngine.on(event as never, cb as never)
      return () => {
        removeLocal()
        removeMock()
      }
    }
    return removeLocal
  }

  send(event: string, payload?: unknown) {
    if (isMockMode()) return
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ event, payload }))
    }
  }

  private dispatch(event: string, payload: unknown) {
    this.handlers.get(event)?.forEach((cb) => cb(payload))
  }
}

export const socket = new SocketClient()
