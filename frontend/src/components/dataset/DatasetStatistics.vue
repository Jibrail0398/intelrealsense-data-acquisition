<script setup lang="ts">
import { onMounted } from 'vue'
import { PhChartBar, PhSpinnerGap } from '@phosphor-icons/vue'

import { useDatasetStore } from '@/stores/datasetStore'

const dataset = useDatasetStore()

onMounted(async () => {
  if (dataset.selectedDatasetId) {
    await dataset.refreshStatistics(dataset.selectedDatasetId)
  }
})

const maxCount = () => Math.max(...(dataset.statistics?.map((c) => c.count) ?? [1]), 1)
</script>

<template>
  <section class="rounded-md border border-zinc-200 bg-white p-4">
    <header class="mb-3 flex items-center justify-between">
      <h3 class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">
        <ChartBar class="h-4 w-4 text-zinc-400" weight="duotone" />
        Dataset Statistics
      </h3>
      <SpinnerGap v-if="dataset.loadingStatistics" class="h-4 w-4 animate-spin text-blue-600" />
    </header>

    <!-- Loading -->
    <div v-if="!dataset.statistics" class="flex flex-col gap-2">
      <div v-for="i in 3" :key="i" class="skeleton h-7 w-full" />
    </div>

    <!-- Empty -->
    <p
      v-else-if="dataset.statistics.length === 0"
      class="rounded-md border border-dashed border-zinc-200 px-3 py-6 text-center text-xs leading-relaxed text-zinc-400"
    >
      No captures recorded for this dataset yet.
      Select a label and take your first shot.
    </p>

    <!-- Data -->
    <template v-else>
      <ul class="flex flex-col gap-2.5">
        <li
          v-for="row in dataset.statistics"
          :key="row.labelName"
          class="grid grid-cols-[1fr_auto] items-center gap-x-3"
        >
          <span class="truncate text-sm text-zinc-700">{{ row.labelName }}</span>
          <span class="font-mono text-sm tabular-nums text-zinc-900">{{ row.count }}</span>
          <span class="col-span-2 h-1 overflow-hidden rounded-full bg-zinc-100">
            <span
              class="block h-full rounded-full bg-accent/70 transition-[width] duration-500 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)]"
              :style="{ width: `${Math.max((row.count / maxCount()) * 100, 1)}%` }"
            />
          </span>
        </li>
      </ul>
      <footer
        class="mt-3 flex items-baseline justify-between border-t border-zinc-100 pt-3"
      >
        <span class="text-xs font-semibold uppercase tracking-wide text-zinc-500">Total</span>
        <span class="font-mono text-lg font-semibold tabular-nums text-zinc-900">
          {{ dataset.totalCaptures }}
        </span>
      </footer>
    </template>
  </section>
</template>
