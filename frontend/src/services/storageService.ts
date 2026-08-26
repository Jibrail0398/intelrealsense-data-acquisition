import { apiRequest, isMockMode } from '@/services/api/client'
import type { BrowsePathResult, StorageInfo } from '@/types'
import { mockEngine } from '@/services/websocket/mockEngine'

function delay<T>(value: T, ms = 400): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), ms))
}

export const storageService = {
  async getInfo(): Promise<StorageInfo> {
    if (isMockMode()) return delay(mockEngine.storageSnapshot())
    return apiRequest<StorageInfo>('/storage')
  },

  async setPath(path: string): Promise<StorageInfo> {
    if (isMockMode()) {
      mockEngine.setStoragePath(path)
      return delay(mockEngine.storageSnapshot(), 200)
    }
    return apiRequest<StorageInfo>('/storage/path', {
      method: 'PUT',
      body: JSON.stringify({ path }),
    })
  },

  async browse(): Promise<BrowsePathResult> {
    if (isMockMode()) {
      const path = await mockEngine.browsePath()
      return { path, canceled: path === null }
    }
    return apiRequest<BrowsePathResult>('/storage/browse')
  },
}
