import type {
  CameraConfig,
  CameraConfigUpdate,
  CameraStatus,
  DepthSample,
  SensorOptions,
  StreamCapabilities,
} from '@/types'

import { api } from './api'

export const cameraService = {
  status: () => api.get<CameraStatus>('/camera/status').then((r) => r.data),
  connect: () => api.post<CameraStatus>('/camera/connect').then((r) => r.data),
  disconnect: () => api.post<CameraStatus>('/camera/disconnect').then((r) => r.data),
  hardwareReset: () => api.post<CameraStatus>('/camera/reset').then((r) => r.data),
  capabilities: () => api.get<StreamCapabilities>('/camera/capabilities').then((r) => r.data),
  config: () => api.get<CameraConfig>('/camera/config').then((r) => r.data),
  updateConfig: (update: CameraConfigUpdate) => api.put<CameraConfig>('/camera/config', update).then((r) => r.data),
  options: () => api.get<SensorOptions[]>('/camera/options').then((r) => r.data),
  setOption: (sensor: string, option: string, value: number) =>
    api.put<SensorOptions[]>('/camera/options', { sensor, option, value }).then((r) => r.data),
  resetOptions: () => api.post<SensorOptions[]>('/camera/options/reset').then((r) => r.data),
  depthAt: (x: number, y: number) =>
    api.get<DepthSample>('/camera/depth', { params: { x, y } }).then((r) => r.data),
}
