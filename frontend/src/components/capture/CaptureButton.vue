<script setup lang="ts">
import { computed } from 'vue'
import { PhCamera as Camera, PhSpinnerGap, PhCheckCircle, PhWarningCircle, PhPauseCircle } from '@phosphor-icons/vue'

import { useCaptureStore } from '@/stores/captureStore'
import { useCameraStore } from '@/stores/cameraStore'

const capture = useCaptureStore()
const camera = useCameraStore()

const isContinuous = computed(() => capture.mode === 'continuous')

const buttonLabel = computed(() => {
  switch (capture.captureState) {
    case 'capturing':
      return 'CAPTURING…'
    case 'disabled':
      return 'CAPTURE UNAVAILABLE'
    default:
      return 'CAPTURE'
  }
})

const disabledHint = computed(() => {
  if (!camera.isConnected) return 'Camera must be connected before capturing.'
  if (!camera.configValid) return 'Camera configuration is invalid.'
  return null
})
</script>

<template>
  <div class="flex flex-col gap-2.5">
    <button
      v-if="!isContinuous || !capture.isCapturing"
      :disabled="capture.captureState !== 'ready'"
      class="group flex h-14 w-full items-center justify-center gap-2.5 rounded-md text-base font-semibold tracking-wide text-white transition-all duration-300 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] active:translate-y-[1px] active:scale-[0.99]"
      :class="
        capture.captureState === 'capturing'
          ? 'bg-blue-700'
          : capture.captureState === 'ready'
            ? 'bg-accent hover:bg-accent-hover shadow-[0_10px_24px_-12px_rgba(37,99,235,0.7)]'
            : 'cursor-not-allowed bg-zinc-300 text-zinc-500'
      "
      @click="capture.start()"
    >
      <SpinnerGap
        v-if="capture.captureState === 'capturing'"
        class="h-5 w-5 animate-spin"
      />
      <Camera v-else class="h-5 w-5 transition-transform duration-300 group-hover:-rotate-6" weight="fill" />
      {{ buttonLabel }}
    </button>

    <button
      v-else
      class="flex h-14 w-full items-center justify-center gap-2.5 rounded-md bg-danger text-base font-semibold tracking-wide text-white shadow-[0_10px_24px_-12px_rgba(220,38,38,0.7)] transition-all duration-300 hover:bg-danger-hover active:translate-y-[1px] active:scale-[0.99]"
      @click="capture.stop()"
    >
      <PauseCircle class="h-5 w-5" weight="fill" />
      STOP
    </button>

    <!-- Success / pair feedback -->
    <div
      v-if="capture.lastCapture && capture.captureState === 'ready'"
      class="flex items-center gap-2 rounded-md border px-3 py-2 text-xs"
      :class="
        capture.isPairBroken
          ? 'border-amber-200 bg-amber-50 text-amber-800'
          : 'border-emerald-200 bg-emerald-50 text-emerald-800'
      "
    >
      <CheckCircle v-if="!capture.isPairBroken" class="h-4 w-4 shrink-0" weight="fill" />
      <WarningCircle v-else class="h-4 w-4 shrink-0" weight="fill" />
      {{
        capture.isPairBroken
          ? 'Last capture has an incomplete RGB/Depth pair.'
          : `Saved ${capture.lastCapture.rgbFilename.split('/')[1]} + ${capture.lastCapture.depthFilename.split('/')[1]}`
      }}
    </div>

    <p v-if="capture.captureState === 'disabled' && disabledHint" class="text-xs text-zinc-400">
      {{ disabledHint }}
    </p>
  </div>
</template>
