import { PhKeyboard } from '@phosphor-icons/vue'
<script setup lang="ts">


defineProps<{ open: boolean }>()
const emit = defineEmits<{ (e: 'close'): void }>()

const shortcuts = [
  { keys: ['Space'], action: 'Capture' },
  { keys: ['R'], action: 'Retake last capture' },
  { keys: ['Delete'], action: 'Delete last capture' },
  { keys: ['S'], action: 'Start / stop continuous capture' },
  { keys: ['Esc'], action: 'Stop capture / close dialogs' },
]

function kbdClass() {
  return [
    'inline-flex min-w-[3.75rem] justify-center rounded border border-zinc-300 bg-zinc-50 px-2 py-1',
    'font-mono text-xs font-medium text-zinc-700 shadow-[inset_0_-2px_0_rgba(24,24,27,0.06)]',
  ]
}
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
        @click.self="emit('close')"
      >
        <div class="w-full max-w-md rounded-lg border border-zinc-200 bg-white shadow-[0_24px_48px_-16px_rgba(24,24,27,0.25)]">
          <header class="flex items-center gap-2.5 border-b border-zinc-200 px-6 py-4">
            <Keyboard class="h-5 w-5 text-zinc-500" weight="duotone" />
            <h2 class="text-sm font-semibold text-zinc-900">Keyboard Shortcuts</h2>
          </header>
          <ul class="divide-y divide-zinc-100 px-6 py-2">
            <li
              v-for="sc in shortcuts"
              :key="sc.action"
              class="flex items-center justify-between gap-4 py-3"
            >
              <span class="text-sm text-zinc-600">{{ sc.action }}</span>
              <kbd :class="kbdClass()">{{ sc.keys[0] }}</kbd>
            </li>
          </ul>
          <footer class="border-t border-zinc-100 px-6 py-3">
            <p class="text-xs text-zinc-400">
              Shortcuts are inactive while typing in an input field.
            </p>
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
