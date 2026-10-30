<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'

import PageHeader from '@/components/common/PageHeader.vue'

const route = useRoute()
const tabs = [
  { to: '/settings/camera', label: 'Camera' },
  { to: '/settings/capture', label: 'Capture rules' },
  { to: '/settings/shortcuts', label: 'Shortcuts' },
]
const current = computed(() => tabs.find((t) => route.path.startsWith(t.to)))
</script>

<template>
  <div>
    <PageHeader :title="current ? `Settings · ${current.label}` : 'Settings'" />
    <nav aria-label="Settings sections" class="mb-7 flex gap-6 overflow-x-auto border-b border-border">
      <RouterLink
        v-for="tab in tabs"
        :key="tab.to"
        :to="tab.to"
        class="flex h-10 shrink-0 items-center transition-colors"
        :class="route.path.startsWith(tab.to) ? 'text-ink' : 'text-subtle hover:text-ink'"
        :aria-current="route.path.startsWith(tab.to) ? 'page' : undefined"
      >
        <span :class="route.path.startsWith(tab.to) && 'selected-line h-10 leading-10'">{{ tab.label }}</span>
      </RouterLink>
    </nav>
    <RouterView />
  </div>
</template>
