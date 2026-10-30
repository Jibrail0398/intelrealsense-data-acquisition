import type { DirectoryEntry, DirectoryListing, PickedDirectory } from '@/types'

import { api } from './api'

export const systemService = {
  // Opens the operating system's folder dialog on the machine running the backend.
  // The user may take minutes, so no timeout.
  pickDirectory: (initial?: string) =>
    api
      .post<PickedDirectory>('/system/pick-directory', null, { params: { initial }, timeout: 0 })
      .then((r) => r.data),
  listDirectory: (path?: string) =>
    api.get<DirectoryListing>('/system/directories', { params: { path } }).then((r) => r.data),
  createDirectory: (parent: string, name: string) =>
    api.post<DirectoryEntry>('/system/directories', { parent, name }).then((r) => r.data),
}
