<script setup lang="ts">
import { RouterLink } from 'vue-router'

import { thumbnailUrl } from '@/constants/api'
import { useCaptureStore } from '@/stores/capture'
import { formatRecent } from '@/utils/format'

const capture = useCaptureStore()
const SLOTS = 5
</script>

<template>
  <section class="rounded-md border border-border bg-surface px-5 pt-4 pb-5 shadow-[var(--shadow)]" aria-labelledby="recent-heading">
    <header class="mb-3 flex items-center justify-between">
      <h2 id="recent-heading" class="text-base font-semibold">Latest shots</h2>
      <RouterLink to="/history" class="text-small text-subtle hover:text-ink">View all</RouterLink>
    </header>

    <ol class="grid grid-cols-2 gap-4 sm:grid-cols-5">
      <li v-for="(shot, i) in capture.recent" :key="shot.id" class="min-w-0" :class="i === 4 && 'hidden sm:block'">
        <img
          :src="thumbnailUrl(shot.id)"
          :alt="shot.image_name"
          class="aspect-[4/3] w-full rounded-sm bg-ground object-cover"
          loading="lazy"
        />
        <p class="mt-1.5 truncate font-mono" :title="shot.image_name">{{ shot.image_name }}</p>
        <p class="truncate text-small text-subtle">{{ formatRecent(shot.captured_at) }}</p>
      </li>
      <li
        v-for="n in Math.max(0, SLOTS - capture.recent.length)"
        :key="`empty-${n}`"
        class="hidden min-w-0 sm:block"
        aria-hidden="true"
      >
        <div class="aspect-[4/3] w-full rounded-sm border border-dashed border-control" />
        <p class="mt-1.5 text-small text-faint">{{ n === 1 && !capture.recent.length ? 'No shots yet' : ' ' }}</p>
        <p class="text-small">&nbsp;</p>
      </li>
    </ol>
  </section>
</template>
