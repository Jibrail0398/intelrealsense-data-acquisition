import { PhWarningOctagon } from '@phosphor-icons/vue'
<script setup lang="ts">


defineProps<{
  open: boolean
  title: string
  message: string
  busy?: boolean
}>()

const emit = defineEmits<{
  (e: 'cancel'): void
  (e: 'confirm'): void
}>()
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-200"
      leave-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="open"
        class="fixed inset-0 z-40 flex items-center justify-center bg-zinc-950/35 p-4 backdrop-blur-[2px]"
        @click.self="emit('cancel')"
      >
        <div
          class="w-full max-w-sm rounded-lg border border-zinc-200 bg-white p-6 shadow-[0_24px_48px_-16px_rgba(24,24,27,0.25)]"
        >
          <div class="flex items-start gap-3">
            <WarningOctagon class="h-5 w-5 shrink-0 text-red-600" weight="duotone" />
            <div>
              <h3 class="text-sm font-semibold text-zinc-900">{{ title }}</h3>
              <p class="mt-1 text-sm leading-relaxed text-zinc-600">{{ message }}</p>
            </div>
          </div>
          <div class="mt-5 flex justify-end gap-2">
            <button
              class="rounded-md border border-zinc-300 px-3.5 py-2 text-sm font-medium text-zinc-700 transition-all duration-300 hover:border-zinc-400 hover:bg-zinc-50 active:scale-[0.98]"
              @click="emit('cancel')"
            >
              Cancel
            </button>
            <button
              :disabled="busy"
              class="rounded-md bg-danger px-3.5 py-2 text-sm font-medium text-white transition-all duration-300 hover:bg-danger-hover active:scale-[0.98] disabled:opacity-60"
              @click="emit('confirm')"
            >
              {{ busy ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
