import type { CaptureResult, CaptureRules, HistoryPage, HistoryQuery, NextName } from '@/types'

import { api } from './api'

export const captureService = {
  // A burst can take a while (count × interval); give it room beyond the default timeout.
  capture: (projectId: number, classId: number) =>
    api
      .post<CaptureResult>('/capture', { project_id: projectId, class_id: classId }, { timeout: 15 * 60_000 })
      .then((r) => r.data),
  nextName: (projectId: number, classId: number) =>
    api
      .get<NextName>('/capture/next-name', { params: { project_id: projectId, class_id: classId } })
      .then((r) => r.data),

  rules: () => api.get<CaptureRules>('/settings/capture-rules').then((r) => r.data),
  saveRules: (rules: CaptureRules) => api.put<CaptureRules>('/settings/capture-rules', rules).then((r) => r.data),

  history: (query: HistoryQuery) => api.get<HistoryPage>('/history', { params: query }).then((r) => r.data),
  removeCapture: (id: number, deleteFiles = true) =>
    api.delete(`/history/${id}`, { params: { delete_files: deleteFiles } }),
}
