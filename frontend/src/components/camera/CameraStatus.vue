<script setup lang="ts">

import { computed } from 'vue'
import { PhCheck, PhX } from '@phosphor-icons/vue'
import { useCameraStore } from '@/stores/cameraStore'

const camera = useCameraStore()

const dotClass = computed(() => {
  switch (camera.status) {
    case 'connected':
      return 'bg-emerald-500'
    case 'connecting':
    case 'reconnecting':
      return 'bg-amber-400'
    case 'error':
      return 'bg-danger'
    default:
      return 'bg-zinc-400'
  }
})

function streamOk(s: string) {
  return s === 'streaming'
}
</script>

<template>
  <div
    class="flex flex-wrap items-center gap-x-5 gap-y-2 rounded-md border border-zinc-200 bg-white px-4 py-3"
  >
    <span class="flex items-center gap-2">
      <span class="relative flex h-2.5 w-2.5">
        <span v-if="camera.isConnected" class="absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-40 pulse-dot" />
        <span class="relative inline-flex h-2.5 w-2.5 rounded-full" :class="dotClass" />
      </span>
      <span class="text-sm font-medium text-zinc-900">{{ camera.statusLabel }}</span>
    </span>

    <span class="hidden h-4 w-px bg-zinc-200 sm:block" />

    <span class="flex items-center gap-1.5 text-xs">
      <span class="font-medium uppercase tracking-wide text-zinc-500">RGB</span>
      <Check v-if="streamOk(camera.rgbStatus)" class="h-3.5 w-3.5 text-emerald-600" weight="bold" />
      <X v-else class="h-3.5 w-3.5 text-zinc-300" weight="bold" />
    </span>
    <span class="flex items-center gap-1.5 text-xs">
      <span class="font-medium uppercase tracking-wide text-zinc-500">Depth</span>
      <Check v-if="streamOk(camera.depthStatus)" class="h-3.5 w-3.5 text-emerald-600" weight="bold" />
      <X v-else class="h-3.5 w-3.5 text-zinc-300" weight="bold" />
    </span>

    <span
      v-if="camera.rgbFrame"
      class="ml-auto hidden font-mono text-xs text-zinc-500 md:block"
    >
      {{ camera.rgbFrame.width }} × {{ camera.rgbFrame.height }} @ {{ camera.rgbFrame.fps }} FPS
    </span>
  </div>
</template>
