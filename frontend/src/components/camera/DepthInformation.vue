<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { PhCrosshair } from '@phosphor-icons/vue'

import { useCameraStore } from '@/stores/cameraStore'

const props = defineProps<{ cursor: { x: number; y: number } }>()

const camera = useCameraStore()
const distance = ref<number | null>(null)
const sampling = ref(false)

const hasCursor = computed(() => props.cursor.x >= 0)

let throttleTimer: ReturnType<typeof setTimeout> | null = null

watch(
  () => [props.cursor.x, props.cursor.y] as const,
  ([x, y]) => {
    if (x < 0 || !camera.isConnected) {
      distance.value = null
      return
    }
    if (throttleTimer !== null) return
    throttleTimer = setTimeout(async () => {
      throttleTimer = null
      sampling.value = true
      try {
        const sample = await camera.sampleDepth(x, y)
        distance.value = sample.distanceMeters
      } finally {
        sampling.value = false
      }
    }, 90)
  },
)

function fmt(v: number | null | undefined, unit = '') {
  return v == null ? '—' : `${v}${unit}`
}
</script>

<template>
  <section class="rounded-md border border-zinc-200 bg-white p-4">
    <header class="mb-3 flex items-center gap-2">
      <Crosshair class="h-4 w-4 text-zinc-400" weight="duotone" />
      <h3 class="text-xs font-semibold uppercase tracking-wide text-zinc-500">
        Depth Information
      </h3>
    </header>

    <dl class="grid grid-cols-2 gap-x-4 gap-y-2 font-mono text-sm">
      <dt class="text-zinc-400">Resolution</dt>
      <dd class="text-right text-zinc-900">
        {{ camera.depthFrame ? `${camera.depthFrame.width} × ${camera.depthFrame.height}` : '—' }}
      </dd>
      <dt class="text-zinc-400">FPS</dt>
      <dd class="text-right text-zinc-900">{{ camera.depthFrame?.fps ?? '—' }}</dd>
      <dt class="text-zinc-400">Min Depth</dt>
      <dd class="text-right text-zinc-900">0.21 m</dd>
      <dt class="text-zinc-400">Max Depth</dt>
      <dd class="text-right text-zinc-900">3.42 m</dd>
    </dl>

    <div class="mt-3 border-t border-zinc-100 pt-3">
      <div v-if="hasCursor" class="flex items-baseline justify-between font-mono text-sm">
        <span class="text-zinc-400">
          X {{ cursor.x }} · Y {{ cursor.y }}
        </span>
        <span
          class="font-semibold tabular-nums"
          :class="distance == null ? 'text-zinc-300' : 'text-blue-700'"
        >
          <template v-if="sampling && distance == null">…</template>
          <template v-else>{{ distance == null ? 'n/a' : `${distance.toFixed(2)} m` }}</template>
        </span>
      </div>
      <p v-else class="text-xs text-zinc-400">
        Hover over the depth preview to probe distance at pixel.
      </p>
      <p class="mt-1.5 text-[11px] uppercase tracking-wide text-zinc-300">
        Unit: meters · invalid pixels show n/a
      </p>
    </div>
  </section>
</template>
