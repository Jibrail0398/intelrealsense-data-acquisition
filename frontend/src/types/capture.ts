import type { FormatKey } from './project'

export type TimerSeconds = 0 | 3 | 5 | 10 | 20

export interface CaptureRules {
  images_per_take: number
  burst_interval_ms: number
  timer_seconds: TimerSeconds
}

export interface CaptureRecord {
  id: number
  project_id: number
  project_name: string
  class_id: number | null
  class_name: string
  image_name: string
  index: number
  files: Partial<Record<FormatKey, string>>
  burst_id: string
  width: number
  height: number
  depth_scale: number
  captured_at: string
}

export interface CaptureResult {
  burst_id: string
  captures: CaptureRecord[]
}

export interface NextName {
  image_name: string
  index: number
  paths: Partial<Record<FormatKey, string>>
}

export interface HistoryPage {
  items: CaptureRecord[]
  total: number
  limit: number
  offset: number
}

export interface HistoryQuery {
  project_id?: number
  class_name?: string
  date_from?: string
  date_to?: string
  q?: string
  limit?: number
  offset?: number
}
