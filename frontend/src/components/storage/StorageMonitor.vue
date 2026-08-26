<script setup lang="ts">

import { useStorageStore } from '@/stores/storageStore'
import { PhWarningCircle } from '@phosphor-icons/vue'

const storage = useStorageStore()
</script>

<template>
  <section class="rounded-md border border-zinc-200 bg-white p-4">
    <header class="mb-3 flex items-center justify-between">
      <h3 class="text-xs font-semibold uppercase tracking-wide text-zinc-500">Storage</h3>
      <span
        v-if="storage.info"
        class="font-mono text-xs tabular-nums text-zinc-400"
      >
        {{ storage.usagePercent.toFixed(0) }}% used
      </span>
    </header>

    <!-- Loading -->
    <div v-if="!storage.info" class="flex flex-col gap-2">
      <div class="skeleton h-4 w-full" />
      <div class="skeleton h-4 w-3/5" />
      <div class="skeleton mt-2 h-1.5 w-full" />
    </div>

    <template v-else>
      <dl class="grid grid-cols-2 gap-x-4 gap-y-1.5 font-mono text-sm tabular-nums">
        <dt class="text-zinc-400">Used by dataset</dt>
        <dd class="text-right text-zinc-900">{{ storage.info.usedByDatasetGb.toFixed(2) }} GB</dd>
        <dt class="text-zinc-400">Available</dt>
        <dd class="text-right" :class="storage.isLowStorage ? 'text-danger' : 'text-zinc-900'">
          {{ storage.info.availableGb.toFixed(1) }} GB
        </dd>
      </dl>

      <div
        class="mt-3 h-1.5 overflow-hidden rounded-full"
        :class="storage.isLowStorage ? 'bg-red-100' : 'bg-zinc-100'"
        role="progressbar"
        aria-label="Dataset storage usage"
        :aria-valuenow="Math.round(storage.usagePercent)"
        aria-valuemin="0"
        aria-valuemax="100"
      >
        <div
          class="h-full rounded-full transition-[width] duration-500 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)]"
          :class="storage.isLowStorage ? 'bg-danger' : 'bg-zinc-500'"
          :style="{ width: `${storage.usagePercent}%` }"
        />
      </div>

      <Transition
        enter-active-class="transition-all duration-300 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)]"
        enter-from-class="opacity-0 -translate-y-1"
      >
        <p
          v-if="storage.isLowStorage"
          class="mt-3 flex items-start gap-1.5 rounded-md border border-red-200 bg-red-50 px-2.5 py-2 text-xs leading-snug text-red-800"
        >
          <WarningCircle class="mt-px h-4 w-4 shrink-0" weight="fill" />
          <span>
            Low storage — only {{ storage.info.availableGb.toFixed(1) }} GB remaining.
            Free space before large burst sessions.
          </span>
        </p>
      </Transition>
    </template>
  </section>
</template>
