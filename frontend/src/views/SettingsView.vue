<script setup lang="ts">
import { onMounted } from 'vue'
import { useCameraStore } from '@/stores/cameraStore'
import { useCaptureStore } from '@/stores/captureStore'
import { useStorageStore } from '@/stores/storageStore'

import AppSelect from '@/components/ui/AppSelect.vue'
import StoragePath from '@/components/storage/StoragePath.vue'
import StorageMonitor from '@/components/storage/StorageMonitor.vue'
import ShortcutsModal from '@/components/ui/ShortcutsModal.vue'
import { ref } from 'vue'

const camera = useCameraStore()
const capture = useCaptureStore()
const storage = useStorageStore()

onMounted(() => {
  camera.init()
  capture.init()
  storage.init()
  if (!camera.options) void camera.loadOptions()
})

function resOptions(list: string[] | undefined) {
  return (list ?? []).map((r) => ({ value: r, label: r.replace('x', ' × ') }))
}
function numOptions(list: number[] | undefined) {
  return (list ?? []).map((n) => ({ value: n, label: `${n}` }))
}
function strOptions(list: string[] | undefined) {
  return (list ?? []).map((v) => ({ value: v, label: v === 'auto' ? 'Auto' : v }))
}

const shortcutsOpen = ref(false)
</script>

<template>
  <div class="grid grid-cols-1 items-start gap-4 xl:grid-cols-[minmax(0,1fr)_380px]">
    <!-- Camera + storage -->
    <div class="flex flex-col gap-4">
      <section
        class="rounded-md border border-zinc-200 bg-white p-5"
        aria-labelledby="camera-settings-heading"
      >
        <header class="mb-4 flex items-center justify-between border-b border-zinc-100 pb-3">
          <h2 id="camera-settings-heading" class="text-sm font-semibold text-zinc-900">Camera</h2>
          <span
            v-if="camera.settingsLoading"
            class="font-mono text-xs text-blue-700"
          >applying… stream will restart</span>
        </header>

        <div v-if="!camera.settings || !camera.options" class="flex flex-col gap-4">
          <div v-for="i in 5" :key="i" class="skeleton h-10 w-full" />
        </div>

        <fieldset
          v-else
          :disabled="capture.isCapturing || camera.settingsLoading"
          class="grid grid-cols-1 gap-4 disabled:opacity-60 sm:grid-cols-2 lg:grid-cols-3"
        >
          <AppSelect
            label="RGB Resolution"
            :model-value="camera.settings.rgbResolution"
            :options="resOptions(camera.options.rgbResolutions)"
            @update:model-value="(v) => camera.updateSettings({ rgbResolution: v })"
          />
          <AppSelect
            label="Depth Resolution"
            :model-value="camera.settings.depthResolution"
            :options="resOptions(camera.options.depthResolutions)"
            @update:model-value="(v) => camera.updateSettings({ depthResolution: v })"
          />
          <AppSelect
            label="FPS"
            :model-value="camera.settings.fps"
            :options="numOptions(camera.options.fpsOptions)"
            @update:model-value="(v) => camera.updateSettings({ fps: Number(v) })"
          />
          <AppSelect
            label="Exposure"
            :model-value="camera.settings.exposure"
            :options="strOptions(camera.options.exposureModes)"
            @update:model-value="(v) => camera.updateSettings({ exposure: v })"
          />
          <AppSelect
            label="White Balance"
            :model-value="camera.settings.whiteBalance"
            :options="strOptions(camera.options.whiteBalanceModes)"
            @update:model-value="(v) => camera.updateSettings({ whiteBalance: v })"
          />
        </fieldset>

        <p
          v-if="!capture.isCapturing && (camera.settings || camera.options)"
          class="mt-4 rounded-md bg-zinc-50 px-3 py-2 text-xs leading-relaxed text-zinc-500 ring-1 ring-inset ring-zinc-200"
        >
          Changing resolution or FPS restarts the live stream. Settings are locked during an active capture.
        </p>
      </section>

      <section class="rounded-md border border-zinc-200 bg-white p-5" aria-labelledby="storage-settings-heading">
        <h2 id="storage-settings-heading" class="mb-4 border-b border-zinc-100 pb-3 text-sm font-semibold text-zinc-900">
          Storage
        </h2>
        <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
          <StoragePath />
          <StorageMonitor />
        </div>
      </section>
    </div>

    <!-- Capture defaults + shortcuts -->
    <aside class="flex flex-col gap-4">
      <section class="rounded-md border border-zinc-200 bg-white p-5" aria-labelledby="defaults-heading">
        <h2 id="defaults-heading" class="mb-4 border-b border-zinc-100 pb-3 text-sm font-semibold text-zinc-900">
          Capture Defaults
        </h2>
        <fieldset :disabled="capture.isCapturing" class="flex flex-col gap-4 disabled:opacity-60">
          <AppSelect
            label="Default Mode"
            v-model="capture.mode"
            :options="[
              { value: 'single', label: 'Single' },
              { value: 'burst', label: 'Burst' },
              { value: 'continuous', label: 'Continuous' },
            ]"
          />
          <label class="flex flex-col gap-2">
            <span class="text-xs font-medium uppercase tracking-wide text-zinc-500">Default Count</span>
            <input
              v-model.number="capture.count"
              type="number"
              min="1"
              class="rounded-md border border-zinc-300 px-3 py-2 font-mono text-sm transition-all duration-300 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600/15"
            />
          </label>
          <label class="flex flex-col gap-2">
            <span class="text-xs font-medium uppercase tracking-wide text-zinc-500">Default Interval</span>
            <div class="relative">
              <input
                v-model.number="capture.intervalMs"
                type="number"
                min="50"
                step="50"
                class="w-full rounded-md border border-zinc-300 py-2 pl-3 pr-11 font-mono text-sm transition-all duration-300 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600/15"
              />
              <span class="absolute right-3 top-1/2 -translate-y-1/2 font-mono text-xs text-zinc-400">ms</span>
            </div>
          </label>
        </fieldset>
      </section>

      <section class="rounded-md border border-zinc-200 bg-white p-5" aria-labelledby="kb-heading">
        <h2 id="kb-heading" class="mb-4 border-b border-zinc-100 pb-3 text-sm font-semibold text-zinc-900">
          Keyboard
        </h2>
        <ul class="divide-y divide-zinc-100 text-sm">
          <li class="flex items-center justify-between py-2.5">
            <span class="text-zinc-600">Capture</span>
            <kbd class="rounded border border-zinc-300 bg-zinc-50 px-2 py-0.5 font-mono text-xs text-zinc-700 shadow-[inset_0_-2px_0_rgba(24,24,27,0.06)]">Space</kbd>
          </li>
          <li class="flex items-center justify-between py-2.5">
            <span class="text-zinc-600">Retake last capture</span>
            <kbd class="rounded border border-zinc-300 bg-zinc-50 px-2 py-0.5 font-mono text-xs text-zinc-700 shadow-[inset_0_-2px_0_rgba(24,24,27,0.06)]">R</kbd>
          </li>
          <li class="flex items-center justify-between py-2.5">
            <span class="text-zinc-600">Start / stop continuous</span>
            <kbd class="rounded border border-zinc-300 bg-zinc-50 px-2 py-0.5 font-mono text-xs text-zinc-700 shadow-[inset_0_-2px_0_rgba(24,24,27,0.06)]">S</kbd>
          </li>
          <li class="flex items-center justify-between py-2.5">
            <span class="text-zinc-600">Stop / cancel</span>
            <kbd class="rounded border border-zinc-300 bg-zinc-50 px-2 py-0.5 font-mono text-xs text-zinc-700 shadow-[inset_0_-2px_0_rgba(24,24,27,0.06)]">Esc</kbd>
          </li>
        </ul>
      </section>

      <button
        class="self-start rounded-md border border-dashed border-zinc-300 px-3 py-2 text-xs font-medium text-zinc-500 transition-all duration-300 hover:border-blue-400 hover:text-blue-700 active:scale-[0.98]"
        @click="shortcutsOpen = true"
      >
        Open shortcuts reference
      </button>
    </aside>

    <ShortcutsModal :open="shortcutsOpen" @close="shortcutsOpen = false" />
  </div>
</template>
