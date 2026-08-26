import type { CameraStatus } from './camera'

export type CaptureMode = 'single' | 'burst' | 'continuous'

export type CaptureState = 'ready' | 'capturing' | 'success' | 'error' | 'disabled'

export interface LastCapture {
  id: string
  datasetName: string
  labelName: string
  rgbFilename: string
  depthFilename: string
  rgbOk: boolean
  depthOk: boolean
  pairOk: boolean
  previewDataUrl?: string
  timestamp?: number
}

export interface CaptureProgressPayload {
  current: number
  total: number | null
}

export interface CaptureCompletedPayload {
  id: string
  datasetName: string
  labelName: string
  rgbFilename: string
  depthFilename: string
  rgbOk: boolean
  depthOk: boolean
  pairOk: boolean
  previewDataUrl?: string
  timestamp: number
}

export interface CaptureFailedPayload {
  reason:
    | 'rgb_save_failed'
    | 'depth_save_failed'
    | 'storage_error'
    | 'camera_error'
    | 'unknown'
  message: string
}

export interface StartCaptureCommand {
  mode: CaptureMode
  count: number | null
  intervalMs: number
  datasetId: string
  labelId: string
}

export interface RetakeResultPayload {
  ok: boolean
  message?: string
}

export type DeleteResultPayload = RetakeResultPayload

export interface CaptureGate {
  cameraStatus: CameraStatus
  storageAvailable: boolean
  hasDataset: boolean
  hasLabel: boolean
  configValid: boolean
}
