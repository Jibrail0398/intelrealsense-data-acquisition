<script setup lang="ts">
import { ref } from 'vue'
import { PhCamera as Camera, PhDatabase as Database, PhGearSix as GearSix, PhKeyboard as Keyboard } from '@phosphor-icons/vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'

import ToastHost from '@/components/ui/ToastHost.vue'
import ShortcutsModal from '@/components/ui/ShortcutsModal.vue'

const route = useRoute()
const shortcutsOpen = ref(false)

const navItems = [
  { to: '/', label: 'Capture', icon: Camera },
  { to: '/dataset', label: 'Dataset', icon: Database },
  { to: '/settings', label: 'Settings', icon: GearSix },
]

function isActive(to: string) {
  return route.path === to
}
</script>

<template>
  <div class="min-h-[100dvh]">
    <header class="sticky top-0 z-20 border-b border-zinc-200 bg-white/85 backdrop-blur-md">
      <div class="mx-auto flex h-14 max-w-[1400px] items-center gap-6 px-4 sm:px-6">
        <RouterLink to="/" class="flex items-center gap-2.5">
          <span class="flex h-7 w-7 items-center justify-center rounded-md bg-zinc-900">
            <Camera class="h-4 w-4 text-white" weight="duotone" />
          </span>
          <span class="text-sm font-semibold tracking-tight text-zinc-900">
            RealSense Collector
            <span class="ml-1.5 hidden font-mono text-[11px] font-normal text-zinc-400 sm:inline">v1.0</span>
          </span>
        </RouterLink>

        <nav class="flex items-center gap-1" aria-label="Primary">
          <RouterLink
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-all duration-300 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] active:scale-[0.97]"
            :class="
              isActive(item.to)
                ? 'bg-zinc-900 text-white'
                : 'text-zinc-500 hover:bg-zinc-100 hover:text-zinc-900'
            "
          >
            <component :is="item.icon" class="h-4 w-4" />
            {{ item.label }}
          </RouterLink>
        </nav>

        <button
          class="ml-auto flex items-center gap-1.5 rounded-md border border-zinc-200 px-2.5 py-1.5 text-xs font-medium text-zinc-500 transition-all duration-300 hover:border-zinc-300 hover:text-zinc-800 active:scale-[0.97]"
          @click="shortcutsOpen = true"
        >
          <Keyboard class="h-4 w-4" />
          <span class="hidden sm:inline">Shortcuts</span>
        </button>
      </div>
    </header>

    <main class="mx-auto w-full max-w-[1400px] px-4 py-6 sm:px-6">
      <RouterView />
    </main>

    <ToastHost />
    <ShortcutsModal :open="shortcutsOpen" @close="shortcutsOpen = false" />
  </div>
</template>
