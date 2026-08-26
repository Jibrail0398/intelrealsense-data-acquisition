import { defineStore } from 'pinia'
import type {
  CameraFramePayload,
  CameraOptionsPayload,
  CameraSettings,
  CameraStatus,
  DepthSamplePayload,
  StreamStatus,
} from '@/types'
import { cameraService } from '@/services/cameraService'
import { socket } from '@/services/websocket/socket'
import { useToastStore } from './toastStore'

interface StreamFrame extends Omit<CameraFramePayload, 'stream' | 'timestamp'> {}

export const useCameraStore = defineStore('camera', {
  state: () => ({
    status: 'connecting' as CameraStatus,
    rgbStatus: 'loading' as StreamStatus,
    depthStatus: 'loading' as StreamStatus,
    rgbFrame: null as StreamFrame | null,
    depthFrame: null as StreamFrame | null,
    settings: null as CameraSettings | null,
    options: null as CameraOptionsPayload | null,
    settingsLoading: false,
    initialized: false,
    backendOffline: false,
  }),

  getters: {
    isConnected: (s) => s.status === 'connected',
    isBusy: (s) => s.status === 'connecting' || s.status === 'reconnecting',
    hasError: (s) => s.status === 'error',
    statusLabel(): string {
      switch (this.status) {
        case 'connected':
          return 'Camera Connected'
        case 'connecting':
          return 'Connecting'
        case 'disconnected':
          return 'Camera Disconnected'
        case 'reconnecting':
          return 'Reconnecting'
        case 'error':
          return 'Camera Error'
      }
    },
    configValid: (s): boolean =>
      !!(s.settings && s.options && s.rgbStatus !== 'error'),
  },

  actions: {
    init() {
      if (this.initialized) return
      this.initialized = true

      const toast = useToastStore()

      socket.connect()

      socket.on('camera.status', (payload) => {
        const data = payload as { status: CameraStatus }
        const prev = this.status
        this.status = data.status
        if (data.status === 'connected') {
          this.backendOffline = false
          if (prev !== 'connected') toast.success('RealSense camera connected.')
          this.rgbStatus = 'loading'
          this.depthStatus = 'loading'
        }
        if (data.status === 'disconnected') {
          toast.error('Unable to connect to RealSense camera.')
        }
        if (data.status === 'reconnecting' && prev === 'connected') {
          toast.warning('Stream restarting — applying camera settings.')
        }
      })

      socket.on('camera.frame', (payload) => {
        if (!cameraService.isFramePayload(payload)) return
        const frame: CameraFramePayload = payload
        const entry = {
          dataUrl: frame.dataUrl,
          width: frame.width,
          height: frame.height,
          fps: frame.fps,
        }
        if (frame.stream === 'rgb') {
          this.rgbFrame = entry
          this.rgbStatus = 'streaming'
        } else {
          this.depthFrame = entry
          this.depthStatus = 'streaming'
        }
      })

      // Backend offline detection for real deployments
      if (!this.options) this.loadOptions()
    },

    async loadOptions() {
      try {
        this.options = await cameraService.getOptions()
        if (!this.settings) await this.loadSettings()
        this.backendOffline = false
      } catch {
        this.backendOffline = true
        useToastStore().error('Unable to communicate with local backend.')
      }
    },

    async loadSettings() {
      try {
        this.settings = await cameraService.getSettings()
      } catch {
        useToastStore().error('Unable to communicate with local backend.')
      }
    },

    async updateSettings(patch: Partial<CameraSettings>) {
      const toast = useToastStore()
      this.settingsLoading = true
      try {
        const result = await cameraService.updateSettings(patch)
        this.settings = { ...(this.settings as CameraSettings), ...patch }
        if (result.restartRequired) {
          toast.info('Applying new stream configuration.')
        }
        return { ok: true as const }
      } catch {
        toast.error('Failed to apply camera settings.')
        return { ok: false as const }
      } finally {
        this.settingsLoading = false
      }
    },

    async sampleDepth(x: number, y: number): Promise<DepthSamplePayload> {
      return cameraService.getDepthSample(x, y)
    },
  },
})
