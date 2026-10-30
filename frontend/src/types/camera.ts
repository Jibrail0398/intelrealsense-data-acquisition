export type CameraStatusValue = 'disconnected' | 'connecting' | 'connected' | 'error'
export type Colormap = 'turbo' | 'jet' | 'inferno' | 'viridis' | 'bone'

export interface StreamProfile {
  width: number
  height: number
  fps: number
}

export interface CameraStatus {
  status: CameraStatusValue
  message: string | null
  backend: 'realsense' | 'mock'
  device: Record<string, string> | null
  color: StreamProfile | null
  depth: StreamProfile | null
  fps: number
}

export interface ResolutionOption {
  width: number
  height: number
  fps: number[]
}

export interface StreamCapabilities {
  color: ResolutionOption[]
  depth: ResolutionOption[]
}

export interface FilterConfig {
  decimation: { enabled: boolean; magnitude: number }
  threshold: { enabled: boolean; min_distance: number; max_distance: number }
  disparity_domain: boolean
  spatial: {
    enabled: boolean
    magnitude: number
    smooth_alpha: number
    smooth_delta: number
    holes_fill: number
  }
  temporal: { enabled: boolean; smooth_alpha: number; smooth_delta: number; persistence: number }
  hole_filling: { enabled: boolean; mode: number }
}

export interface PreviewConfig {
  colormap: Colormap
  min_distance: number
  max_distance: number
}

export interface CameraConfig {
  color: StreamProfile
  depth: StreamProfile
  align_to_color: boolean
  filters: FilterConfig
  preview: PreviewConfig
  options: Record<string, Record<string, number>>
}

export type CameraConfigUpdate = Partial<Omit<CameraConfig, 'options'>>

export interface OptionChoice {
  value: number
  label: string
}

export interface SensorOption {
  name: string
  label: string
  description: string
  value: number
  min: number
  max: number
  step: number
  default: number
  read_only: boolean
  kind: 'bool' | 'choice' | 'range'
  choices: OptionChoice[] | null
}

export interface SensorOptions {
  key: string
  name: string
  options: SensorOption[]
}

export interface DepthSample {
  x: number
  y: number
  distance_m: number
}
