export type CameraStatus =
  | 'connected'
  | 'connecting'
  | 'disconnected'
  | 'error'
  | 'reconnecting'

export type StreamStatus = 'idle' | 'loading' | 'streaming' | 'error'

export interface ResolutionOption {
  width: number
  height: number
}

export interface CameraSettings {
  rgbResolution: string
  depthResolution: string
  fps: number
  exposure: string
  whiteBalance: string
}

export interface CameraOptionsPayload {
  rgbResolutions: string[]
  depthResolutions: string[]
  fpsOptions: number[]
  exposureModes: string[]
  whiteBalanceModes: string[]
}

export interface CameraFramePayload {
  stream: 'rgb' | 'depth'
  dataUrl: string
  width: number
  height: number
  fps: number
  timestamp: number
}

export interface DepthSamplePayload {
  x: number
  y: number
  distanceMeters: number | null
}
