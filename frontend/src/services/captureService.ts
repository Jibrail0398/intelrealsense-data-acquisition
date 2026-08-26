import { apiRequest, isMockMode } from '@/services/api/client'
import type {
  CaptureMode,
  DeleteResultPayload,
  RetakeResultPayload,
  StartCaptureCommand,
} from '@/types'
import { mockEngine } from '@/services/websocket/mockEngine'
import { socket } from '@/services/websocket/socket'

export const captureService = {
  start(cmd: StartCaptureCommand) {
    if (isMockMode()) {
      mockEngine.startCapture(cmd)
      return
    }
    socket.send('capture.start', cmd)
  },

  stop() {
    if (isMockMode()) {
      mockEngine.stopCapture(true)
      return
    }
    socket.send('capture.stop')
  },

  isCapturing(): boolean {
    return isMockMode() ? mockEngine.isCapturing() : false
  },

  async deleteCapture(id: string, datasetId: string, labelId: string): Promise<DeleteResultPayload> {
    if (isMockMode()) return mockEngine.deleteCapture(id, datasetId, labelId)
    return apiRequest<DeleteResultPayload>(`/captures/${id}`, { method: 'DELETE' })
  },

  async retake(id: string, datasetId: string, labelId: string): Promise<RetakeResultPayload> {
    if (isMockMode()) return mockEngine.retakeCapture(id)
    return apiRequest<RetakeResultPayload>(`/captures/${id}/retake`, {
      method: 'POST',
      body: JSON.stringify({ datasetId, labelId }),
    })
  },

  modeLabel(mode: CaptureMode): string {
    switch (mode) {
      case 'single':
        return 'Single frame per operation'
      case 'burst':
        return 'Fixed number of frames with interval'
      case 'continuous':
        return 'Runs until stopped manually'
    }
  },
}
