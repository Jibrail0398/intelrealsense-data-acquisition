import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { FALLBACK_FORMATS } from '@/constants/capture'
import { eventSocket } from '@/services/eventSocket'
import { projectService } from '@/services/projectService'
import type { OutputFormat, Project, ProjectCreate, ProjectUpdate } from '@/types'

export const useProjectStore = defineStore('projects', () => {
  const projects = ref<Project[]>([])
  const formats = ref<OutputFormat[]>(FALLBACK_FORMATS)
  const activeProjectId = ref<number | null>(null)
  const activeClassId = ref<number | null>(null)
  const loaded = ref(false)
  const loadError = ref<string | null>(null)

  const activeProject = computed(() => projects.value.find((p) => p.id === activeProjectId.value) ?? null)
  const activeClass = computed(
    () => activeProject.value?.classes.find((c) => c.id === activeClassId.value) ?? null,
  )

  let started = false

  async function init() {
    if (started) return
    started = true
    eventSocket.on('project.updated', ({ id }: { id: number }) => void refreshProject(id))
    eventSocket.on('project.deleted', ({ id }: { id: number }) => dropProject(id))
    eventSocket.on('capture.completed', () => activeProjectId.value && void refreshProject(activeProjectId.value))
    eventSocket.on('capture.deleted', ({ project_id }: { project_id: number }) => void refreshProject(project_id))
    await load()
  }

  async function load() {
    try {
      const [list, fmts, session] = await Promise.all([
        projectService.list(),
        projectService.formats(),
        projectService.session(),
      ])
      projects.value = list
      formats.value = fmts
      activeProjectId.value = list.some((p) => p.id === session.active_project_id) ? session.active_project_id : null
      activeClassId.value = activeProjectId.value ? session.active_class_id : null
      loadError.value = null
    } catch (err) {
      loadError.value = err instanceof Error ? err.message : String(err)
    } finally {
      loaded.value = true
    }
  }

  function upsert(project: Project) {
    const i = projects.value.findIndex((p) => p.id === project.id)
    if (i === -1) projects.value.unshift(project)
    else projects.value.splice(i, 1, project)
    if (project.id === activeProjectId.value && !project.classes.some((c) => c.id === activeClassId.value)) {
      activeClassId.value = project.classes[0]?.id ?? null
    }
  }

  function dropProject(id: number) {
    projects.value = projects.value.filter((p) => p.id !== id)
    if (activeProjectId.value === id) {
      activeProjectId.value = null
      activeClassId.value = null
    }
  }

  async function refreshProject(id: number) {
    try {
      upsert(await projectService.get(id))
    } catch {
      dropProject(id)
    }
  }

  async function persistSession() {
    const saved = await projectService.saveSession({
      active_project_id: activeProjectId.value,
      active_class_id: activeClassId.value,
    })
    activeClassId.value = saved.active_class_id
  }

  async function selectProject(id: number | null) {
    activeProjectId.value = id
    activeClassId.value = null
    await persistSession()
  }

  async function selectClass(id: number) {
    activeClassId.value = id
    await persistSession()
  }

  function stepClass(delta: 1 | -1) {
    const classes = activeProject.value?.classes ?? []
    if (!classes.length) return
    const i = classes.findIndex((c) => c.id === activeClassId.value)
    const next = classes[(i + delta + classes.length) % classes.length]!
    void selectClass(next.id)
  }

  async function create(data: ProjectCreate) {
    const project = await projectService.create(data)
    upsert(project)
    await selectProject(project.id)
    return project
  }

  async function update(id: number, data: ProjectUpdate) {
    const project = await projectService.update(id, data)
    upsert(project)
    return project
  }

  async function remove(id: number, deleteFiles = false) {
    const result = await projectService.remove(id, deleteFiles)
    dropProject(id)
    return result
  }

  async function addClass(id: number, name: string) {
    upsert(await projectService.addClass(id, name))
  }

  async function renameClass(id: number, classId: number, name: string) {
    upsert(await projectService.renameClass(id, classId, name))
  }

  async function removeClass(id: number, classId: number) {
    upsert(await projectService.removeClass(id, classId))
  }

  async function moveClass(id: number, classId: number, delta: 1 | -1) {
    const project = projects.value.find((p) => p.id === id)
    if (!project) return
    const ids = project.classes.map((c) => c.id)
    const i = ids.indexOf(classId)
    const j = i + delta
    if (i < 0 || j < 0 || j >= ids.length) return
    ;[ids[i], ids[j]] = [ids[j]!, ids[i]!]
    upsert(await projectService.reorderClasses(id, ids))
  }

  return {
    projects, formats, activeProjectId, activeClassId, loaded, loadError,
    activeProject, activeClass,
    init, load, refreshProject, selectProject, selectClass, stepClass,
    create, update, remove, addClass, renameClass, removeClass, moveClass,
  }
})
