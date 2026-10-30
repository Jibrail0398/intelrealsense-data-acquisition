<script setup lang="ts">
import { computed } from 'vue'

import { useCameraStore } from '@/stores/camera'

const camera = useCameraStore()

const tone = computed(() => {
  if (!camera.backendOnline) return 'bg-negative'
  switch (camera.status?.status) {
    case 'connected':
      return 'bg-positive'
    case 'connecting':
      return 'bg-warning'
    case 'error':
      return 'bg-negative'
    default:
      return 'bg-faint'
  }
})
</script>

<template>
  <span class="inline-block size-2 shrink-0 rounded-full" :class="tone" aria-hidden="true" />
</template>
