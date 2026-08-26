export interface DatasetInfo {
  id: string
  name: string
}

export interface LabelInfo {
  id: string
  name: string
  datasetId: string
}

export interface LabelCount {
  labelId: string
  labelName: string
  count: number
}

export interface DatasetStatistics {
  datasetId: string
  counts: LabelCount[]
  total: number
}

export interface RecentCaptureEntry {
  id: string
  labelName: string
  rgbFilename: string
  depthFilename: string
  pairOk: boolean
  timestamp: number
}
