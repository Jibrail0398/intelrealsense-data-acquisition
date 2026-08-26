<script setup lang="ts">

import { useCameraStore } from '@/stores/cameraStore'
import { PhWarningCircle } from '@phosphor-icons/vue'

const camera = useCameraStore()
</script>

<template>
  <figure class="flex flex-col gap-2.5">
    <div
      class="relative aspect-[4/3] overflow-hidden rounded-md border border-zinc-200 bg-white"
    >
      <Transition
        enter-active-class="transition-opacity duration-300"
        enter-from-class="opacity-0"
        leave-active-class="transition-opacity duration-300"
        leave-to-class="opacity-0"
      >
        <img
          v-if="camera.status === 'connected' && camera.rgbFrame"
          :src="camera.rgbFrame.dataUrl"
          alt="Live RGB stream from RealSense camera"
          class="h-full w-full object-cover"
        />
      </Transition>

      <div
        v-if="camera.rgbStatus !== 'streaming'"
        class="absolute inset-0 flex items-center justify-center"
      >
        <div v-if="camera.rgbStatus === 'error'" class="flex items-center gap-2 text-sm text-red-600">
          <WarningCircle class="h-4 w-4" weight="fill" />
          RGB stream unavailable.
        </div>
        <div v-else class="skeleton scanline h-full w-full !rounded-none">
          <span class="sr-only">Waiting for RGB stream…</span>
        </div>
      </div>

      <figcaption
        v-if="camera.rgbFrame"
        class="absolute bottom-2 left-2 rounded bg-zinc-950/60 px-2 py-1 font-mono text-[11px] leading-none text-white backdrop-blur-sm"
      >
        RGB · {{ camera.rgbFrame.width }}×{{ camera.rgbFrame.height }} · {{ camera.rgbFrame.fps }} FPS
      </figcaption>
    </div>
    <p class="text-xs font-medium uppercase tracking-wide text-zinc-500">RGB Stream</p>
  </figure>
</template>
