<script setup lang="ts">
import { RefreshCw } from '@lucide/vue'
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'

import CameraStatusDot from '@/components/common/CameraStatusDot.vue'
import { Button } from '@/components/ui/button'
import { useDepthProbe } from '@/composables/useDepthProbe'
import { errorMessage } from '@/services/api'
import { useCameraStore } from '@/stores/camera'
import { useCaptureStore } from '@/stores/capture'

import StreamTile from './StreamTile.vue'

const camera = useCameraStore()
const capture = useCaptureStore()
const { reading, probe, clear } = useDepthProbe()
const actionError = ref<string | null>(null)

const color = computed(() => camera.status?.color ?? camera.config?.color ?? { width: 640, height: 480, fps: 30 })
const depth = computed(() => camera.status?.depth ?? camera.config?.depth ?? { width: 640, height: 480, fps: 30 })
const aligned = computed(() => camera.config?.align_to_color ?? true)
// The depth array the backend samples is colour-sized when aligned.
const depthFrame = computed(() => (aligned.value ? color.value : depth.value))

const statusLine = computed(() => {
  if (!camera.backendOnline) return 'Backend offline'
  const s = camera.status
  if (!s) return 'Checking camera…'
  if (s.status === 'connected') {
    const sim = s.backend === 'mock' ? ' (simulated)' : ''
    return `${s.device?.name ?? 'RealSense'}${sim} · serial ${s.device?.serial_number ?? '—'} · USB ${s.device?.usb_type ?? '—'}`
  }
  return s.message ?? 'Camera not connected'
})

const statusTitle = computed(() => {
  switch (camera.status?.status) {
    case 'connected':
      return 'Camera connected'
    case 'connecting':
      return 'Connecting'
    case 'error':
      return 'Camera error'
    default:
      return 'Camera not connected'
  }
})

async function reconnect() {
  try {
    await camera.connect()
    actionError.value = null
  } catch (err) {
    actionError.value = errorMessage(err)
  }
}
</script>

<template>
  <section class="flex flex-col rounded-md border border-border bg-surface px-5 pt-4 pb-5 shadow-[var(--shadow)]" aria-labelledby="camera-heading">
    <header class="mb-4 flex flex-wrap items-center justify-between gap-x-4 gap-y-1">
      <h2 id="camera-heading" class="flex items-center gap-2 text-base font-semibold">
        <CameraStatusDot />{{ camera.backendOnline ? statusTitle : 'Backend offline' }}
      </h2>
      <p class="min-w-0 truncate text-small text-subtle" :title="statusLine">{{ statusLine }}</p>
    </header>

    <div class="grid flex-1 gap-4 sm:grid-cols-2">
      <StreamTile
        kind="rgb"
        label="RGB"
        :live="camera.isConnected"
        :nonce="camera.streamNonce"
        :width="color.width"
        :height="color.height"
      >
        <template #meta>{{ color.width }}×{{ color.height }} · {{ color.fps }} fps</template>
        <template #offline>
          <div class="grid justify-items-center gap-3">
            <p>{{ statusLine }}</p>
            <div v-if="camera.backendOnline && camera.status?.status !== 'connecting'" class="flex gap-2">
              <Button size="sm" variant="outline" @click="reconnect"><RefreshCw />Connect</Button>
              <Button size="sm" variant="ghost" as-child><RouterLink to="/settings/camera">Camera settings</RouterLink></Button>
            </div>
            <p v-if="actionError" class="text-negative">{{ actionError }}</p>
          </div>
        </template>
        <template #overlay>
          <div
            v-if="capture.countdown !== null"
            class="absolute top-3 right-3 grid size-16 place-items-center rounded-full bg-[rgba(19,18,23,0.82)] text-[40px] leading-none font-semibold num"
            role="timer"
            aria-live="assertive"
          >
            {{ capture.countdown }}
          </div>
        </template>
      </StreamTile>

      <StreamTile
        kind="depth"
        label="Depth"
        :live="camera.isConnected"
        :nonce="camera.streamNonce"
        :width="depthFrame.width"
        :height="depthFrame.height"
        @pointer="(e) => camera.isConnected && probe(e, depthFrame.width, depthFrame.height)"
        @leave="clear"
      >
        <template #meta>
          <template v-if="reading">{{ reading.metres ? `${reading.metres.toFixed(3)} m` : 'no depth' }} at {{ reading.x }}, {{ reading.y }}</template>
          <template v-else>{{ depth.width }}×{{ depth.height }} · {{ depth.fps }} fps{{ aligned ? ' · aligned to RGB' : '' }}</template>
        </template>
        <template #offline><span /></template>
      </StreamTile>
    </div>
  </section>
</template>
