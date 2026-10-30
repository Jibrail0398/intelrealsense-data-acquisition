<script setup lang="ts">
import type { SaveState } from '@/composables/useAutoSave'

defineProps<{ state: SaveState; error?: string | null }>()
</script>

<template>
  <span class="text-small" role="status" aria-live="polite">
    <span v-if="state === 'saving'" class="text-subtle">Saving…</span>
    <span v-else-if="state === 'saved'" class="text-subtle">Saved</span>
    <span v-else-if="state === 'error'" class="text-negative">{{ error ?? 'Not saved' }}</span>
  </span>
</template>
