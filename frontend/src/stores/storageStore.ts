import { defineStore } from 'pinia'
import { storageService } from '@/services/storageService'
import { socket } from '@/services/websocket/socket'
import { useToastStore } from './toastStore'

export const useStorageStore = defineStore('storage', {
  state: () => ({
    info: null as {
      path: string
      availableGb: number
      usedByDatasetGb: number
      lowStorageThresholdGb: number
    } | null,
    loading: false,
    settingPath: false,
    initialized: false,
  }),

  getters: {
    isAvailable: (s) => !!s.info && s.info.path.length > 0,
    isLowStorage(): boolean {
      return !!this.info && this.info.availableGb < this.info.lowStorageThresholdGb
    },
    usagePercent(): number {
      if (!this.info) return 0
      const used = Math.max(this.info.availableGb, 1)
      const ratio = this.info.usedByDatasetGb / (used + this.info.usedByDatasetGb)
      return Math.min(Math.max(ratio * 100, 2), 100)
    },
  },

  actions: {
    init() {
      if (this.initialized) return
      this.initialized = true
      socket.on('storage.updated', (payload) => {
        this.info = payload as NonNullable<typeof this.info>
      })
      void this.refresh()
    },

    async refresh() {
      this.loading = !this.info
      try {
        this.info = await storageService.getInfo()
      } catch {
        useToastStore().error('Failed to read storage information.')
      } finally {
        this.loading = false
      }
    },

    async browseAndSet() {
      const toast = useToastStore()
      this.settingPath = true
      try {
        const result = await storageService.browse()
        if (!result.path || result.canceled) return
        this.info = await storageService.setPath(result.path)
        toast.success(`Storage path set to ${result.path}`)
      } catch {
        toast.error('Unable to save dataset. Check storage path.')
      } finally {
        this.settingPath = false
      }
    },

    async setManualPath(path: string) {
      const toast = useToastStore()
      if (!path.trim()) return
      this.settingPath = true
      try {
        this.info = await storageService.setPath(path.trim())
        toast.success('Storage path updated.')
      } catch {
        toast.error('Unable to save dataset. Check storage path.')
      } finally {
        this.settingPath = false
      }
    },
  },
})
