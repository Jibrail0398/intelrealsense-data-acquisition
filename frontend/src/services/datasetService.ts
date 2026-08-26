import { apiRequest, isMockMode } from '@/services/api/client'
import type {
  DatasetInfo,
  DatasetStatistics,
  LabelInfo,
  RecentCaptureEntry,
} from '@/types'
import { mockEngine } from '@/services/websocket/mockEngine'

function delay<T>(value: T, ms = 350): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), ms))
}

export const datasetService = {
  async getDatasets(): Promise<DatasetInfo[]> {
    if (isMockMode()) return delay(mockEngine.datasets.map((d) => ({ ...d })))
    return apiRequest<DatasetInfo[]>('/datasets')
  },

  async getLabels(datasetId: string): Promise<LabelInfo[]> {
    if (isMockMode()) {
      return delay(
        mockEngine.labels.filter((l) => l.datasetId === datasetId).map((l) => ({ ...l })),
      )
    }
    return apiRequest<LabelInfo[]>(`/datasets/${datasetId}/labels`)
  },

  async createLabel(datasetId: string, name: string): Promise<LabelInfo> {
    if (isMockMode()) {
      const label: LabelInfo = {
        id: `lb-${name.toLowerCase().replace(/\s+/g, '-')}-${Date.now().toString(36)}`,
        name,
        datasetId,
      }
      mockEngine.labels.push(label)
      mockEngine.statistics[datasetId] ??= {}
      mockEngine.statistics[datasetId][label.id] ??= 0
      return delay(label)
    }
    return apiRequest<LabelInfo>(`/datasets/${datasetId}/labels`, {
      method: 'POST',
      body: JSON.stringify({ name }),
    })
  },

  async getStatistics(datasetId: string): Promise<DatasetStatistics> {
    if (isMockMode()) {
      const counts = Object.entries(mockEngine.statistics[datasetId] ?? {}).map(
        ([labelId, count]) => ({
          labelId,
          labelName:
            mockEngine.labels.find((l) => l.id === labelId)?.name ?? labelId,
          count,
        }),
      )
      return delay({
        datasetId,
        counts,
        total: counts.reduce((sum, c) => sum + c.count, 0),
      })
    }
    return apiRequest<DatasetStatistics>(`/datasets/${datasetId}/statistics`)
  },

  async getRecentCaptures(datasetId: string, labelId: string): Promise<RecentCaptureEntry[]> {
    if (isMockMode()) {
      return delay(
        mockEngine
          .getRecentCaptures(datasetId, labelId)
          .map(({ datasetId: _d, labelId: _l, ...rest }) => rest),
      )
    }
    return apiRequest<RecentCaptureEntry[]>(
      `/datasets/${datasetId}/labels/${labelId}/captures`,
    )
  },
}
