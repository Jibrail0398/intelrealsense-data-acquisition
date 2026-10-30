import { defineStore } from 'pinia'
import { computed, reactive, ref } from 'vue'

import { errorMessage } from '@/services/api'
import { captureService } from '@/services/captureService'
import type { CaptureRecord, HistoryQuery } from '@/types'
import { addDays, startOfDay } from '@/utils/format'

export type RangePreset = 'today' | '7d' | '30d' | 'all' | 'custom'

const PAGE_SIZE = 50

export const useHistoryStore = defineStore('history', () => {
  const filters = reactive({
    projectId: null as number | null,
    className: null as string | null,
    range: 'all' as RangePreset,
    from: '', // YYYY-MM-DD, local time, used when range is "custom"
    to: '',
    q: '',
  })
  const items = ref<CaptureRecord[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastLoaded = ref<Date | null>(null)

  const hasMore = computed(() => items.value.length < total.value)

  function timeWindow(): { date_from?: string; date_to?: string } {
    const today = startOfDay(new Date())
    switch (filters.range) {
      case 'today':
        return { date_from: today.toISOString() }
      case '7d':
        return { date_from: addDays(today, -6).toISOString() }
      case '30d':
        return { date_from: addDays(today, -29).toISOString() }
      case 'custom': {
        const out: { date_from?: string; date_to?: string } = {}
        if (filters.from) out.date_from = new Date(`${filters.from}T00:00:00`).toISOString()
        if (filters.to) out.date_to = addDays(new Date(`${filters.to}T00:00:00`), 1).toISOString()
        return out
      }
      default:
        return {}
    }
  }

  function query(offset: number): HistoryQuery {
    return {
      ...timeWindow(),
      project_id: filters.projectId ?? undefined,
      class_name: filters.className ?? undefined,
      q: filters.q.trim() || undefined,
      limit: PAGE_SIZE,
      offset,
    }
  }

  async function load() {
    loading.value = true
    try {
      const page = await captureService.history(query(0))
      items.value = page.items
      total.value = page.total
      error.value = null
      lastLoaded.value = new Date()
    } catch (err) {
      error.value = errorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function loadMore() {
    if (loading.value || !hasMore.value) return
    loading.value = true
    try {
      const page = await captureService.history(query(items.value.length))
      items.value.push(...page.items)
      total.value = page.total
    } catch (err) {
      error.value = errorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function remove(id: number) {
    await captureService.removeCapture(id)
    items.value = items.value.filter((i) => i.id !== id)
    total.value = Math.max(0, total.value - 1)
  }

  return { filters, items, total, loading, error, lastLoaded, hasMore, load, loadMore, remove }
})
