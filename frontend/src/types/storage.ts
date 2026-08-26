export interface StorageInfo {
  path: string
  availableGb: number
  usedByDatasetGb: number
  lowStorageThresholdGb: number
}

export interface BrowsePathResult {
  path: string | null
  canceled?: boolean
}
