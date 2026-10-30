import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { toast } from 'vue-sonner'

import { errorMessage } from '@/services/api'
import { captureService } from '@/services/captureService'
import { eventSocket } from '@/services/eventSocket'
import type { CaptureRecord, CaptureRules, NextName } from '@/types'
import { plural } from '@/utils/format'

import { useCameraStore } from './camera'
import { useProjectStore } from './projects'

const RECENT_LIMIT = 5

export const useCaptureStore = defineStore('capture', () => {
  const rules = ref<CaptureRules>({ images_per_take: 1, burst_interval_ms: 200, timer_seconds: 0 })
  const countdown = ref<number | null>(null)
  const busy = ref(false)
  const progress = ref<{ done: number; total: number } | null>(null)
  const recent = ref<CaptureRecord[]>([])
  const nextName = ref<NextName | null>(null)

  let timer: number | null = null
  let started = false

  async function init() {
    if (started) return
    started = true
    const projects = useProjectStore()
    eventSocket.on('capture.progress', (p: { done: number; total: number }) => {
      progress.value = { done: p.done, total: p.total }
    })
    eventSocket.on('settings.capture_rules', (r: CaptureRules) => (rules.value = r))
    eventSocket.on('capture.deleted', () => void refreshContext())
    watch(
      () => [projects.activeProjectId, projects.activeClassId, projects.activeClass?.name],
      () => void refreshContext(),
    )
    try {
      rules.value = await captureService.rules()
    } catch {
      /* backend offline; defaults stay until it returns */
    }
    await refreshContext()
  }

  async function refreshContext() {
    const projects = useProjectStore()
    const pid = projects.activeProjectId
    const cid = projects.activeClassId
    if (!pid) {
      recent.value = []
      nextName.value = null
      return
    }
    const [page, next] = await Promise.allSettled([
      captureService.history({ project_id: pid, limit: RECENT_LIMIT }),
      cid ? captureService.nextName(pid, cid) : Promise.resolve(null),
    ])
    recent.value = page.status === 'fulfilled' ? page.value.items : []
    nextName.value = next.status === 'fulfilled' ? next.value : null
  }

  async function saveRules(next: CaptureRules) {
    rules.value = await captureService.saveRules(next)
  }

  function blockedReason(): string | null {
    const projects = useProjectStore()
    const camera = useCameraStore()
    if (!projects.activeProject) return 'Create or select a project first'
    if (!projects.activeClass) return 'Choose a class first'
    if (!projects.activeProject.formats.length) return 'Select at least one output format'
    if (!camera.isConnected) return 'Camera is not connected'
    return null
  }

  /** Space / the Capture button: start the countdown, or shoot at once when the timer is off. */
  function trigger() {
    if (busy.value || countdown.value !== null) return
    const reason = blockedReason()
    if (reason) {
      toast.error(reason)
      return
    }
    if (rules.value.timer_seconds > 0) {
      countdown.value = rules.value.timer_seconds
      timer = window.setInterval(() => {
        if (countdown.value === null) return
        countdown.value -= 1
        if (countdown.value <= 0) {
          stopTimer()
          void run()
        }
      }, 1000)
    } else {
      void run()
    }
  }

  function cancel() {
    if (countdown.value === null) return
    stopTimer()
    toast('Countdown cancelled')
  }

  function stopTimer() {
    if (timer) clearInterval(timer)
    timer = null
    countdown.value = null
  }

  async function run() {
    const projects = useProjectStore()
    const project = projects.activeProject
    const cls = projects.activeClass
    if (!project || !cls) return
    busy.value = true
    progress.value = { done: 0, total: rules.value.images_per_take }
    try {
      const result = await captureService.capture(project.id, cls.id)
      const shots = result.captures
      const first = shots[0]?.image_name
      const last = shots[shots.length - 1]?.image_name
      toast.success(shots.length > 1 ? `Saved ${first} to ${last}` : `Saved ${first}`, {
        description: `${plural(shots.length, 'image')} in ${cls.name} · ${project.formats.join(', ')}`,
      })
    } catch (err) {
      toast.error('Capture failed', { description: errorMessage(err) })
    } finally {
      busy.value = false
      progress.value = null
      await refreshContext()
    }
  }

  return {
    rules, countdown, busy, progress, recent, nextName,
    init, refreshContext, saveRules, blockedReason, trigger, cancel,
  }
})
