import { defineStore } from 'pinia'

export interface Toast {
  id: number
  kind: 'error' | 'success' | 'warning' | 'info'
  message: string
}

let nextId = 1

export const useToastStore = defineStore('toast', {
  state: () => ({
    toasts: [] as Toast[],
  }),
  actions: {
    push(kind: Toast['kind'], message: string, ttl = 4200) {
      const id = nextId++
      this.toasts.push({ id, kind, message })
      setTimeout(() => this.dismiss(id), ttl)
    },
    error(message: string) {
      this.push('error', message)
    },
    success(message: string) {
      this.push('success', message)
    },
    warning(message: string) {
      this.push('warning', message)
    },
    info(message: string) {
      this.push('info', message)
    },
    dismiss(id: number) {
      this.toasts = this.toasts.filter((t) => t.id !== id)
    },
  },
})
