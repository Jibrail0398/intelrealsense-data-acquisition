<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import 'vue-sonner/style.css'

import { Toaster } from '@/components/ui/sonner'
import { TooltipProvider } from '@/components/ui/tooltip'
import { useCameraStore } from '@/stores/camera'
import { useCaptureStore } from '@/stores/capture'
import { useProjectStore } from '@/stores/projects'

const camera = useCameraStore()
const projects = useProjectStore()
const capture = useCaptureStore()

onMounted(async () => {
  await Promise.allSettled([camera.init(), projects.init()])
  await capture.init()
})
</script>

<template>
  <TooltipProvider :delay-duration="300">
    <RouterView />
    <Toaster position="bottom-right" theme="dark" :offset="24" />
  </TooltipProvider>
</template>
