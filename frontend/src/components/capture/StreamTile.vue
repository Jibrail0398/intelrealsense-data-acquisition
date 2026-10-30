<script setup lang="ts">
import { ref, watch } from 'vue'

import { streamUrl } from '@/constants/api'

const props = defineProps<{
  kind: 'rgb' | 'depth'
  label: string
  live: boolean
  nonce: number
  width: number
  height: number
}>()
const emit = defineEmits<{ pointer: [event: MouseEvent]; leave: [] }>()

const broken = ref(false)
watch(() => props.nonce, () => (broken.value = false))
</script>

<template>
  <figure class="flex min-w-0 flex-col">
    <div
      class="relative flex-1 overflow-hidden rounded-sm bg-ground"
      :style="{ aspectRatio: `${width} / ${height}` }"
      @mousemove="(e) => emit('pointer', e)"
      @mouseleave="emit('leave')"
    >
      <img
        v-if="live && !broken"
        :key="nonce"
        :src="streamUrl(kind, nonce)"
        :alt="`Live ${label} preview`"
        class="absolute inset-0 size-full object-contain"
        draggable="false"
        @error="broken = true"
      />
      <div v-else class="absolute inset-0 grid place-items-center px-6 text-center text-subtle">
        <slot name="offline">{{ broken ? 'Preview interrupted' : 'No signal' }}</slot>
      </div>
      <slot name="overlay" />
    </div>
    <figcaption class="mt-2 flex items-center justify-between gap-3 text-small">
      <span class="text-ink">{{ label }}</span>
      <span class="num text-subtle"><slot name="meta" /></span>
    </figcaption>
  </figure>
</template>
