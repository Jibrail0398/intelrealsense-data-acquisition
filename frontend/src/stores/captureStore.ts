import { defineStore } from 'pinia'
import type {
  CaptureCompletedPayload,
  CaptureFailedPayload,
  CaptureMode,
  LastCapture,
} from '@/types'
import { captureService } from '@/services/captureService'
import { socket } from '@/services/websocket/socket'
import { useCameraStore } from './cameraStore'
import { useDatasetStore } from './datasetStore'
import { useStorageStore } from './storageStore'
import { useToastStore } from './toastStore'

const FAILURE_MESSAGES: Record<CaptureFailedPayload['reason'], string> = {
  rgb_save_failed: 'Capture failed. RGB frame could not be saved.',
  depth_save_failed: 'Capture failed. Depth frame could not be saved.',
  storage_error: 'Unable to save dataset. Check storage path.',
  camera_error: 'Capture failed. Camera is not available.',
  unknown: 'Capture failed.',
}

export const useCaptureStore = defineStore('capture', {
  state: () => ({
    mode: 'burst' as CaptureMode,
    count: 10,
    intervalMs: 200,
    isCapturing: false,
    progressCurrent: 0,
    progressTotal: null as number | null,
    lastCapture: null as LastCapture | null,
    retaking: false,
    deleting: false,

    initialized: false,
  }),

  getters: {
    captureState(state): 'ready' | 'capturing' | 'success' | 'error' | 'disabled' {
      if (state.isCapturing) return 'capturing'
      const camera = useCameraStore()
      const dataset = useDatasetStore()
      const storage = useStorageStore()
      const blocked =
        !camera.isConnected ||
        !storage.isAvailable ||
        !dataset.selectedLabelId ||
        !camera.configValid
      return blocked ? 'disabled' : 'ready'
    },
    isPairBroken: (s) =>
      !!s.lastCapture && !s.lastCapture.pairOk,
    progressPercent(): number {
      if (this.progressTotal === null || this.progressTotal === 0) return 0
      return Math.round((this.progressCurrent / this.progressTotal) * 100)
    },
  },

  actions: {
    init() {
      if (this.initialized) return
      this.initialized = true
      const toast = useToastStore()
      const camera = useCameraStore()

      socket.on('capture.started', () => {
        this.isCapturing = true
        this.progressCurrent = 0
      })

      socket.on('capture.progress', (payload) => {
        const data = payload as { current: number; total: number | null }
        this.progressCurrent = data.current
        this.progressTotal = data.total
      })

      socket.on('capture.completed', (payload) => {
        const data = payload as CaptureCompletedPayload
        this.lastCapture = {
          id: data.id,
          datasetName: data.datasetName,
          labelName: data.labelName,
          rgbFilename: data.rgbFilename,
          depthFilename: data.depthFilename,
          rgbOk: data.rgbOk,
          depthOk: data.depthOk,
          pairOk: data.pairOk,
          previewDataUrl: data.previewDataUrl,
          timestamp: data.timestamp,
        }
        if (!data.pairOk) {
          toast.warning('Incomplete pair saved — depth file missing for this capture.')
        }
      })

      socket.on('capture.failed', (payload) => {
        const data = payload as CaptureFailedPayload
        this.isCapturing = false
        toast.error(FAILURE_MESSAGES[data.reason] ?? data.message)
      })

      // Auto-stop capture when the camera drops mid-session
      socket.on('camera.status', (payload) => {
        const data = payload as { status: string }
        if (this.isCapturing && data.status !== 'connected') {
          captureService.stop()
          this.isCapturing = false
          toast.error('Capture aborted — camera disconnected.')
        }
      })
    },

    start() {
      const dataset = useDatasetStore()
      if (this.captureState !== 'ready') return
      this.progressCurrent = 0
      this.progressTotal =
        this.mode === 'single' ? 1 : this.mode === 'burst' ? this.count : null
      captureService.start({
        mode: this.mode,
        count: this.mode === 'burst' ? this.count : null,
        intervalMs: this.intervalMs,
        datasetId: dataset.selectedDatasetId as string,
        labelId: dataset.selectedLabelId as string,
      })
      this.isCapturing = true
    },

    stop() {
      captureService.stop()
      this.isCapturing = false
    },

    async retake() {
      const cap = this.lastCapture
      const dataset = useDatasetStore()
      const toast = useToastStore()
      if (!cap || this.retaking || this.isCapturing) return
      this.retaking = true
      try {
        const res = await captureService.retake(
          cap.id,
          dataset.selectedDatasetId ?? '',
          dataset.selectedLabelId ?? '',
        )
        if (res.ok) {
          this.lastCapture = null
          toast.success(`Capture ${cap.id} marked for replacement. Take a new shot.`)
        } else {
          toast.error(res.message ?? 'Retake failed.')
        }
      } catch {
        toast.error('Retake failed — backend unreachable.')
      } finally {
        this.retaking = false
      }
    },

    async removeLast() {
      const cap = this.lastCapture
      const dataset = useDatasetStore()
      const toast = useToastStore()
      if (!cap || this.deleting || this.isCapturing) return
      this.deleting = true
      try {
        const res = await captureService.deleteCapture(
          cap.id,
          dataset.selectedDatasetId ?? '',
          dataset.selectedLabelId ?? '',
        )
        if (res.ok) {
          this.lastCapture = null
          toast.success(`Capture ${cap.id} deleted.`)
        } else {
          toast.error(res.message ?? 'Delete failed.')
        }
      } catch {
        toast.error('Delete failed — backend unreachable.')
      } finally {
        this.deleting = false
      }
    },
  },
})
