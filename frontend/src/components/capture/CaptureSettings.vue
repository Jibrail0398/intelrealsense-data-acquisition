<script setup lang="ts">
import { computed } from 'vue'
import { useCaptureStore } from '@/stores/captureStore'

const capture = useCaptureStore()

const modes = [
  { value: 'single', label: 'Single' },
  { value: 'burst', label: 'Burst' },
  { value: 'continuous', label: 'Continuous' },
] as const

const countError = computed(() => {
  if (capture.mode !== 'burst') return undefined
  if (!Number.isFinite(capture.count)) return 'Enter a number of frames.'
  if (capture.count < 1) return 'Minimum is 1 frame.'
  if (!Number.isInteger(capture.count)) return 'Must be a whole number.'
  return undefined
})

const intervalError = computed(() => {
  if (capture.mode === 'single') return undefined
  if (capture.intervalMs < 50) return 'Minimum interval is 50 ms.'
  if (capture.intervalMs > 10000) return 'Maximum interval is 10000 ms.'
  return undefined
})
</script>

<template>
  <section class="flex flex-col gap-4">
    <fieldset :disabled="capture.isCapturing" class="flex flex-col gap-4 disabled:opacity-60">
      <div class="flex flex-col gap-2">
        <span class="text-xs font-medium uppercase tracking-wide text-zinc-500">Capture Mode</span>
        <div class="grid grid-cols-3 gap-1 rounded-md border border-zinc-300 bg-zinc-100 p-1">
          <button
            v-for="m in modes"
            :key="m.value"
            type="button"
            class="rounded-[5px] px-2 py-1.5 text-sm font-medium transition-all duration-300 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)]"
            :class="
              capture.mode === m.value
                ? 'bg-white text-zinc-900 shadow-[0_1px_3px_rgba(24,24,27,0.12)]'
                : 'text-zinc-500 hover:text-zinc-800'
            "
            @click="capture.mode = m.value"
          >
            {{ m.label }}
          </button>
        </div>
      </div>

      <label v-if="capture.mode === 'burst'" class="flex flex-col gap-2">
        <span class="text-xs font-medium uppercase tracking-wide text-zinc-500">Number of Captures</span>
        <input
          v-model.number="capture.count"
          type="number"
          min="1"
          step="1"
          class="rounded-md border px-3 py-2 font-mono text-sm transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-600/15"
          :class="countError ? 'border-red-400 focus:border-red-500' : 'border-zinc-300 focus:border-blue-600'"
        />
        <p v-if="countError" class="text-xs text-red-600">{{ countError }}</p>
        <p v-else class="font-mono text-xs text-zinc-400">
          → {{ Math.max(capture.count, 0) }} RGB images · {{ Math.max(capture.count, 0) }} Depth files
        </p>
      </label>

      <label v-if="capture.mode !== 'single'" class="flex flex-col gap-2">
        <span class="text-xs font-medium uppercase tracking-wide text-zinc-500">Capture Interval</span>
        <div class="relative">
          <input
            v-model.number="capture.intervalMs"
            type="number"
            min="50"
            max="10000"
            step="50"
            class="w-full rounded-md border py-2 pl-3 pr-11 font-mono text-sm transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-600/15"
            :class="intervalError ? 'border-red-400 focus:border-red-500' : 'border-zinc-300 focus:border-blue-600'"
          />
          <span class="absolute right-3 top-1/2 -translate-y-1/2 font-mono text-xs text-zinc-400">ms</span>
        </div>
        <p v-if="intervalError" class="text-xs text-red-600">{{ intervalError }}</p>
      </label>
    </fieldset>
    <p v-if="capture.isCapturing" class="text-xs text-amber-700">
      Configuration is locked while a capture is running.
    </p>
  </section>
</template>
