<script setup lang="ts">
import { onMounted, watch } from 'vue'

import DeviceSettings from '@/components/settings/DeviceSettings.vue'
import FilterSettings from '@/components/settings/FilterSettings.vue'
import PreviewSettings from '@/components/settings/PreviewSettings.vue'
import SensorSettings from '@/components/settings/SensorSettings.vue'
import StreamSettings from '@/components/settings/StreamSettings.vue'
import { useCameraStore } from '@/stores/camera'

const camera = useCameraStore()

async function refresh() {
  await Promise.allSettled([camera.loadConfig(), camera.loadCapabilities(), camera.loadSensors()])
}

onMounted(refresh)
// Option values and supported profiles come from the device, so re-read them on (re)connect.
watch(() => camera.isConnected, (connected) => connected && refresh())
</script>

<template>
  <div class="divide-y divide-border">
    <DeviceSettings />
    <StreamSettings />
    <SensorSettings />
    <FilterSettings />
    <PreviewSettings />
  </div>
</template>
