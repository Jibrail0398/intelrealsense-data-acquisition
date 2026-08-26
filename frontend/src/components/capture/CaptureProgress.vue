<script setup lang="ts">
import { computed } from 'vue'
import { useCaptureStore } from '@/stores/captureStore'

const capture = useCaptureStore()

const label = computed(() =>
  capture.progressTotal === null
    ? `Frame ${capture.progressCurrent}`
    : `Capturing ${capture.progressCurrent} / ${capture.progressTotal}`,
)
</script>

<template>
  <Transition
    enter-active-class="transition-all duration-300 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)]"
    enter-from-class="opacity-0 -translate-y-1"
    leave-active-class="transition-all duration-200"
    leave-to-class="opacity-0 -translate-y-1"
  >
    <section
      v-if="capture.isCapturing"
      aria-live="polite"
      class="rounded-md border border-blue-200 bg-blue-50/70 p-4"
    >
      <header class="mb-2 flex items-baseline justify-between">
        <h3 class="text-xs font-semibold uppercase tracking-wide text-blue-800">
          Capture in progress
        </h3>
        <span class="font-mono text-sm tabular-nums text-blue-900">{{ label }}</span>
      </header>

      <div
        class="h-1.5 overflow-hidden rounded-full bg-blue-100"
        role="progressbar"
        :aria-valuenow="capture.progressCurrent"
        aria-valuemin="0"
      >
        <div
          class="h-full rounded-full bg-accent transition-[width] duration-200 ease-out"
          :style="{ width: `${Math.max(capture.progressPercent, 4)}%` }"
        />
      </div>

      <p v-if="capture.progressTotal === null" class="mt-2 font-mono text-xs text-blue-800/80">
        Continuous mode — press S or ESC to stop.
      </p>
    </section>
  </Transition>
</template>
