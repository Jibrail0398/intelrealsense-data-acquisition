<script setup lang="ts">
import { ref } from 'vue'
import { PhWarningCircle } from '@phosphor-icons/vue'

import { useCameraStore } from '@/stores/cameraStore'

const emit = defineEmits<{
  (e: 'hover', payload: { x: number; y: number }): void
}>()

const camera = useCameraStore()
const imgEl = ref<HTMLImageElement | null>(null)

function onMouseMove(evt: MouseEvent) {
  const img = imgEl.value
  if (!img || camera.depthStatus !== 'streaming') return
  const rect = img.getBoundingClientRect()
  const x = Math.round(((evt.clientX - rect.left) / rect.width) * (camera.depthFrame?.width ?? 640))
  const y = Math.round(((evt.clientY - rect.top) / rect.height) * (camera.depthFrame?.height ?? 480))
  emit('hover', { x: Math.max(0, x), y: Math.max(0, y) })
}

function onMouseLeave() {
  emit('hover', { x: -1, y: -1 })
}
</script>

<template>
  <figure class="flex flex-col gap-2.5">
    <div
      class="relative aspect-[4/3] overflow-hidden rounded-md border border-zinc-200 bg-white"
    >
      <img
        v-if="camera.status === 'connected' && camera.depthFrame"
        ref="imgEl"
        :src="camera.depthFrame.dataUrl"
        alt="Live depth stream from RealSense camera"
        class="h-full w-full object-cover"
        @mousemove="onMouseMove"
        @mouseleave="onMouseLeave"
      />

      <div
        v-if="camera.depthStatus !== 'streaming'"
        class="absolute inset-0 flex items-center justify-center"
      >
        <div v-if="camera.depthStatus === 'error'" class="flex items-center gap-2 text-sm text-red-600">
          <WarningCircle class="h-4 w-4" weight="fill" />
          Depth frame unavailable.
        </div>
        <div v-else class="skeleton scanline h-full w-full !rounded-none">
          <span class="sr-only">Waiting for depth stream…</span>
        </div>
      </div>

      <figcaption
        v-if="camera.depthFrame"
        class="absolute bottom-2 left-2 rounded bg-zinc-950/60 px-2 py-1 font-mono text-[11px] leading-none text-white backdrop-blur-sm"
      >
        DEPTH · {{ camera.depthFrame.width }}×{{ camera.depthFrame.height }} · {{ camera.depthFrame.fps }} FPS
      </figcaption>

      <span
        v-if="camera.depthStatus === 'streaming'"
        class="absolute right-2 top-2 flex items-center gap-1.5 rounded bg-zinc-950/60 px-2 py-1 font-mono text-[11px] leading-none text-emerald-300 backdrop-blur-sm"
      >
        <span class="h-1.5 w-1.5 rounded-full bg-emerald-400 pulse-dot" />
        VALID
      </span>
    </div>
    <p class="text-xs font-medium uppercase tracking-wide text-zinc-500">Depth Stream</p>
  </figure>
</template>
