import type {
  OutputFormat,
  Project,
  ProjectCreate,
  ProjectDeleteResult,
  ProjectUpdate,
  SessionState,
} from '@/types'

import { api } from './api'

export const projectService = {
  formats: () => api.get<OutputFormat[]>('/formats').then((r) => r.data),
  list: () => api.get<Project[]>('/projects').then((r) => r.data),
  get: (id: number) => api.get<Project>(`/projects/${id}`).then((r) => r.data),
  create: (data: ProjectCreate) => api.post<Project>('/projects', data).then((r) => r.data),
  update: (id: number, data: ProjectUpdate) => api.patch<Project>(`/projects/${id}`, data).then((r) => r.data),
  remove: (id: number, deleteFiles: boolean) =>
    api
      .delete<ProjectDeleteResult>(`/projects/${id}`, { params: { delete_files: deleteFiles } })
      .then((r) => r.data),

  addClass: (id: number, name: string) =>
    api.post<Project>(`/projects/${id}/classes`, { name }).then((r) => r.data),
  renameClass: (id: number, classId: number, name: string) =>
    api.patch<Project>(`/projects/${id}/classes/${classId}`, { name }).then((r) => r.data),
  removeClass: (id: number, classId: number) =>
    api.delete<Project>(`/projects/${id}/classes/${classId}`).then((r) => r.data),
  reorderClasses: (id: number, classIds: number[]) =>
    api.put<Project>(`/projects/${id}/classes/order`, { class_ids: classIds }).then((r) => r.data),

  session: () => api.get<SessionState>('/session').then((r) => r.data),
  saveSession: (state: SessionState) => api.put<SessionState>('/session', state).then((r) => r.data),
}
