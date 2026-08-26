<script setup lang="ts">

import { useToastStore } from '@/stores/toastStore'
import { PhXCircle, PhWarningCircle, PhCheckCircle, PhInfo } from '@phosphor-icons/vue'

const toastStore = useToastStore()

const styles = {
  error: { icon: PhXCircle, ring: 'border-red-200', tint: 'text-red-600' },
  warning: { icon: PhWarningCircle, ring: 'border-amber-200', tint: 'text-amber-600' },
  success: { icon: PhCheckCircle, ring: 'border-emerald-200', tint: 'text-emerald-600' },
  info: { icon: PhInfo, ring: 'border-blue-200', tint: 'text-blue-600' },
} as const
</script>

<template>
  <div class="fixed bottom-5 right-5 z-50 flex w-[22rem] max-w-[calc(100vw-2.5rem)] flex-col gap-2 pointer-events-none">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toastStore.toasts"
        :key="toast.id"
        class="pointer-events-auto flex items-start gap-2.5 rounded-md border bg-white px-3.5 py-3 shadow-[0_8px_24px_-8px_rgba(24,24,27,0.18)]"
        :class="styles[toast.kind].ring"
      >
        <component
          :is="styles[toast.kind].icon"
          class="mt-px h-[18px] w-[18px] shrink-0"
          :class="styles[toast.kind].tint"
          weight="fill"
        />
        <p class="flex-1 text-sm leading-snug text-zinc-800">{{ toast.message }}</p>
        <button
          class="shrink-0 rounded p-0.5 text-zinc-400 transition-colors hover:text-zinc-700 active:scale-95"
          aria-label="Dismiss notification"
          @click="toastStore.dismiss(toast.id)"
        >
          <PhXCircle class="h-4 w-4" weight="regular" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>
