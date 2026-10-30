export type FormatKey = 'jpg' | 'png' | 'tiff' | 'png16' | 'npy'

export interface OutputFormat {
  key: FormatKey
  label: string
  kind: 'rgb' | 'depth'
  folder: string
  ext: string
  description: string
}

export interface ProjectClass {
  id: number
  name: string
  position: number
  count: number
}

export interface Project {
  id: number
  name: string
  destination_dir: string
  formats: FormatKey[]
  classes: ProjectClass[]
  total_captures: number
  created_at: string
  updated_at: string
}

export interface ProjectCreate {
  name: string
  destination_dir: string
  formats: FormatKey[]
  classes: string[]
}

export interface ProjectUpdate {
  name?: string
  destination_dir?: string
  formats?: FormatKey[]
}

export interface ProjectDeleteResult {
  deleted_captures: number
  deleted_files: number
  deleted_folders: number
  errors: string[]
}

export interface SessionState {
  active_project_id: number | null
  active_class_id: number | null
}
