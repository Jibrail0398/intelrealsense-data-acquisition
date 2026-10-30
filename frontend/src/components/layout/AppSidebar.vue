<script setup lang="ts">
import { Camera, History, Settings2 } from '@lucide/vue'
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import CameraStatusDot from '@/components/common/CameraStatusDot.vue'
import { useCameraStore } from '@/stores/camera'

import BrandMark from './BrandMark.vue'

const route = useRoute()
const camera = useCameraStore()

const items = [
  { to: '/capture', label: 'Capture', icon: Camera },
  { to: '/history', label: 'History', icon: History },
  { to: '/settings', label: 'Settings', icon: Settings2 },
]

const isActive = (to: string) => route.path.startsWith(to)

const cameraLabel = computed(() => {
  if (!camera.backendOnline) return 'Offline'
  switch (camera.status?.status) {
    case 'connected':
      return 'Live'
    case 'connecting':
      return 'Starting'
    case 'error':
      return 'Error'
    default:
      return 'No camera'
  }
})
</script>

<template>
  <!-- Desktop and tablet: a labelled rail. Phone: a bottom bar with the same items. -->
  <nav
    aria-label="Main"
    class="fixed inset-x-0 bottom-0 z-30 flex h-16 items-stretch border-t border-border bg-ground md:inset-y-0 md:left-0 md:right-auto md:h-auto md:w-[var(--rail-width)] md:flex-col md:border-t-0 md:border-r"
  >
    <RouterLink
      to="/capture"
      class="hidden h-16 items-center justify-center md:flex"
      aria-label="RealSense Collector, capture"
    >
      <BrandMark />
    </RouterLink>

    <div class="flex flex-1 md:flex-none md:flex-col md:gap-1 md:pt-2">
      <RouterLink
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        :aria-current="isActive(item.to) ? 'page' : undefined"
        class="group flex flex-1 flex-col items-center justify-center gap-1.5 py-2 transition-colors md:h-14 md:flex-none"
        :class="isActive(item.to) ? 'text-ink' : 'text-subtle hover:text-ink'"
      >
        <component :is="item.icon" class="size-[18px]" :stroke-width="1.5" />
        <span class="text-small leading-none" :class="isActive(item.to) && 'selected-line pb-1'">{{ item.label }}</span>
      </RouterLink>
    </div>

    <RouterLink
      to="/settings/camera"
      class="hidden flex-col items-center gap-1.5 pb-5 text-subtle transition-colors hover:text-ink md:mt-auto md:flex"
      :title="camera.status?.message ?? cameraLabel"
    >
      <CameraStatusDot />
      <span class="text-small leading-none">{{ cameraLabel }}</span>
    </RouterLink>
  </nav>
</template>
