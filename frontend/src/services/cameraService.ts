import { apiRequest, isMockMode } from '@/services/api/client'
import type { CameraFramePayload, CameraOptionsPayload, CameraSettings, DepthSamplePayload } from '@/types'
import { mockEngine } from '@/services/websocket/mockEngine'

function delay<T>(value: T, ms = 300): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), ms))
}

export const cameraService = {
  async getOptions(): Promise<CameraOptionsPayload> {
    if (isMockMode()) return delay({ ...mockEngine.options })
    return apiRequest<CameraOptionsPayload>('/camera/options')
  },

  async getSettings(): Promise<CameraSettings> {
    if (isMockMode()) return delay({ ...mockEngine.settings })
    return apiRequest<CameraSettings>('/camera/settings')
  },

  async updateSettings(settings: Partial<CameraSettings>): Promise<{ restartRequired: boolean }> {
    if (isMockMode()) return mockEngine.applySettings(settings)
    return apiRequest<{ restartRequired: boolean }>('/camera/settings', {
      method: 'PUT',
      body: JSON.stringify(settings),
    })
  },

  async getDepthSample(x: number, y: number): Promise<DepthSamplePayload> {
    if (isMockMode()) {
      return delay(
        { x, y, distanceMeters: mockEngine.getDepthSample(x, y) },
        0,
      )
    }
    return apiRequest<DepthSamplePayload>(`/depth/sample?x=${x}&y=${y}`)
  },

  isFramePayload(payload: unknown): payload is CameraFramePayload {
    return (
      typeof payload === 'object' &&
      payload !== null &&
      'stream' in payload &&
      'dataUrl' in payload
    )
  },
}
