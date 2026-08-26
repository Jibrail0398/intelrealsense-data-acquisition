<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useCameraStore } from '@/stores/cameraStore'
import { useCaptureStore } from '@/stores/captureStore'
import { useDatasetStore } from '@/stores/datasetStore'
import { useStorageStore } from '@/stores/storageStore'

import CameraStatus from '@/components/camera/CameraStatus.vue'
import RGBPreview from '@/components/camera/RGBPreview.vue'
import DepthPreview from '@/components/camera/DepthPreview.vue'
import DepthInformation from '@/components/camera/DepthInformation.vue'
import DatasetSelector from '@/components/dataset/DatasetSelector.vue'
import LabelSelector from '@/components/dataset/LabelSelector.vue'
import CaptureSettings from '@/components/capture/CaptureSettings.vue'
import CaptureButton from '@/components/capture/CaptureButton.vue'
import CaptureProgress from '@/components/capture/CaptureProgress.vue'
import LastCaptureCard from '@/components/capture/LastCapture.vue'
import StorageMonitor from '@/components/storage/StorageMonitor.vue'
import { useDashboardShortcuts } from '@/composables/useDashboardShortcuts'

const camera = useCameraStore()
const capture = useCaptureStore()
const dataset = useDatasetStore()
const storage = useStorageStore()

const cursor = ref({ x: -1, y: -1 })

onMounted(() => {
  camera.init()
  capture.init()
  dataset.init()
  storage.init()
})

useDashboardShortcuts({
  capture: () => capture.start(),
  retake: () => void capture.retake(),
  deleteLast: () => void capture.removeLast(),
  stop: () => capture.stop(),
  toggleContinuous: () => {
    if (capture.isCapturing) {
      capture.stop()
    } else {
      capture.mode = 'continuous'
      capture.start()
    }
  },
})
</script>

<template>
  <div class="flex flex-col gap-4">
    <CameraStatus />

    <div class="grid grid-cols-1 items-start gap-4 xl:grid-cols-[minmax(0,1fr)_380px]">
      <!-- Preview zone -->
      <section class="flex flex-col gap-4">
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <RGBPreview />
          <DepthPreview @hover="cursor = $event" />
        </div>
        <DepthInformation :cursor="cursor" />
      </section>

      <!-- Control panel -->
      <aside class="flex flex-col gap-4 rounded-md border border-zinc-200 bg-white p-5">
        <header class="flex flex-col gap-3 border-b border-zinc-100 pb-4">
          <h2 class="text-sm font-semibold text-zinc-900">Capture Configuration</h2>
          <DatasetSelector />
          <LabelSelector />
        </header>

        <div class="border-b border-zinc-100 pb-4">
          <CaptureSettings />
        </div>

        <CaptureButton />
        <CaptureProgress />
        <LastCaptureCard />
        <StorageMonitor />
      </aside>
    </div>
  </div>
</template>
