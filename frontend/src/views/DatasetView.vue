<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { PhFileImage, PhSpinnerGap, PhDatabase } from '@phosphor-icons/vue'

import { useDatasetStore } from '@/stores/datasetStore'
import { datasetService } from '@/services/datasetService'
import type { RecentCaptureEntry } from '@/types'

const dataset = useDatasetStore()
const recent = ref<RecentCaptureEntry[] | null>(null)
const loadingRecent = ref(false)
let recentToken = 0

async function loadRecent() {
  if (!dataset.selectedDatasetId || !dataset.selectedLabelId) {
    recent.value = []
    return
  }
  const token = ++recentToken
  loadingRecent.value = true
  try {
    const entries = await datasetService.getRecentCaptures(
      dataset.selectedDatasetId,
      dataset.selectedLabelId,
    )
    if (token === recentToken) recent.value = entries
  } catch {
    if (token === recentToken) recent.value = []
  } finally {
    if (token === recentToken) loadingRecent.value = false
  }
}

watch(
  () => [dataset.selectedDatasetId, dataset.selectedLabelId] as const,
  () => void loadRecent(),
)

onMounted(async () => {
  dataset.init()
  if (dataset.selectedDatasetId) {
    await dataset.refreshStatistics(dataset.selectedDatasetId)
  }
  await loadRecent()
})

const selectedLabelName = computed(() => dataset.selectedLabel?.name ?? '')
const datasetName = computed(() => dataset.selectedDataset?.name ?? '')

function fmtTime(ts: number) {
  return new Date(ts).toLocaleString([], {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <header class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 class="text-lg font-semibold tracking-tight text-zinc-900">
          Dataset Browser
        </h1>
        <p class="mt-0.5 text-sm text-zinc-500">
          {{ datasetName || 'No dataset selected' }}
          <template v-if="selectedLabelName"> · {{ selectedLabelName }}</template>
        </p>
      </div>
      <div class="w-full max-w-xs">
        <select
            :value="dataset.selectedDatasetId ?? ''"
            class="w-full appearance-none rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm transition-all duration-300 hover:border-zinc-400 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600/15"
            @change="dataset.selectDataset(($event.target as HTMLSelectElement).value)"
          >
            <option v-for="d in dataset.datasets" :key="d.id" :value="d.id">
              {{ d.name }}
            </option>
          </select>
      </div>
    </header>

    <div class="grid grid-cols-1 items-start gap-4 xl:grid-cols-[minmax(0,380px)_minmax(0,1fr)]">
      <!-- Counts table -->
      <section class="rounded-md border border-zinc-200 bg-white" aria-label="Capture counts per label">
        <header class="grid grid-cols-[1fr_auto] gap-x-6 border-b border-zinc-100 px-5 py-3">
          <span class="text-xs font-semibold uppercase tracking-wide text-zinc-500">Label</span>
          <span class="text-right text-xs font-semibold uppercase tracking-wide text-zinc-500">Count</span>
        </header>

        <div v-if="!dataset.statistics" class="flex flex-col gap-2.5 p-5">
          <div v-for="i in 4" :key="i" class="skeleton h-6 w-full" />
        </div>

        <p
          v-else-if="dataset.statistics.length === 0"
          class="px-5 py-10 text-center text-sm leading-relaxed text-zinc-400"
        >
          No captures recorded for this dataset yet.
          Head to the Capture page and take your first shot.
        </p>

        <ul v-else class="divide-y divide-zinc-100">
          <li
            v-for="row in dataset.statistics"
            :key="row.labelName"
            class="grid cursor-pointer grid-cols-[1fr_auto] items-center gap-x-6 px-5 py-3 transition-colors duration-200 hover:bg-zinc-50"
            :class="
              row.labelName === selectedLabelName ? 'bg-blue-50/60' : ''
            "
            @click="
              dataset.selectLabel(
                dataset.labels.find((l) => l.name === row.labelName)?.id ??
                  dataset.selectedLabelId ??
                  '',
              )
            "
          >
            <span class="truncate text-sm font-medium" :class="row.labelName === selectedLabelName ? 'text-blue-800' : 'text-zinc-800'">
              {{ row.labelName }}
            </span>
            <span class="font-mono text-sm tabular-nums text-zinc-700">{{ row.count }}</span>
          </li>
        </ul>

        <footer
          v-if="dataset.statistics && dataset.statistics.length > 0"
          class="flex items-baseline justify-between border-t border-zinc-100 bg-zinc-50/60 px-5 py-3"
        >
          <span class="text-xs font-semibold uppercase tracking-wide text-zinc-500">Total</span>
          <span class="font-mono text-base font-semibold tabular-nums text-zinc-900">
            {{ dataset.totalCaptures }}
          </span>
        </footer>
      </section>

      <!-- Captures of selected label -->
      <section aria-label="Captures in selected label" class="rounded-md border border-zinc-200 bg-white p-5">
        <header class="mb-4 flex items-center justify-between border-b border-zinc-100 pb-3">
          <h2 class="flex items-center gap-2 text-sm font-semibold text-zinc-900">
            <Database class="h-4 w-4 text-zinc-400" weight="duotone" />
            Captures — {{ selectedLabelName }}
          </h2>
          <SpinnerGap v-if="loadingRecent" class="h-4 w-4 animate-spin text-blue-600" />
        </header>

        <div v-if="recent === null || loadingRecent" class="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-4">
          <div v-for="i in 8" :key="i" class="skeleton h-24 w-full" />
        </div>

        <div
          v-else-if="recent.length === 0"
          class="flex flex-col items-center justify-center gap-2 rounded-md border border-dashed border-zinc-200 px-4 py-14 text-center"
        >
          <FileImage class="h-6 w-6 text-zinc-300" weight="duotone" />
          <p class="text-sm text-zinc-400">No captures for this label yet.</p>
          <p class="max-w-[32ch] text-xs leading-relaxed text-zinc-400">
            Select a different label or capture new frames from the dashboard.
          </p>
        </div>

        <ul v-else class="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-4">
          <li
            v-for="entry in recent"
            :key="entry.id"
            class="group rounded-md border p-3 transition-all duration-300 hover:-translate-y-0.5"
            :class="entry.pairOk ? 'border-zinc-200 hover:border-blue-300' : 'border-amber-300 bg-amber-50/40'"
          >
            <p class="font-mono text-sm font-semibold tabular-nums text-zinc-900">
              {{ entry.id }}
            </p>
            <p class="mt-1 truncate font-mono text-[11px] text-zinc-400">{{ entry.rgbFilename }}</p>
            <p class="truncate font-mono text-[11px] text-zinc-400">{{ entry.depthFilename }}</p>
            <p class="mt-1.5 flex items-center justify-between font-mono text-[11px]">
              <span class="text-zinc-400">{{ fmtTime(entry.timestamp) }}</span>
              <span :class="entry.pairOk ? 'text-emerald-600' : 'text-amber-700'">
                {{ entry.pairOk ? 'PAIR OK' : 'NO PAIR' }}
              </span>
            </p>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>
