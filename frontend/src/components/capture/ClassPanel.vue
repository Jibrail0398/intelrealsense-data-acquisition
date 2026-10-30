<script setup lang="ts">
import { computed } from 'vue'

import Kbd from '@/components/common/Kbd.vue'
import { useProjectStore } from '@/stores/projects'
import { formatCount, plural } from '@/utils/format'

const emit = defineEmits<{ edit: [] }>()
const projects = useProjectStore()
const classes = computed(() => projects.activeProject?.classes ?? [])
const total = computed(() => classes.value.reduce((sum, c) => sum + c.count, 0))
</script>

<template>
  <section class="rounded-md border border-border bg-surface px-5 pt-4 pb-4 shadow-[var(--shadow)]" aria-labelledby="class-heading">
    <header class="mb-2 flex items-center justify-between">
      <h2 id="class-heading" class="text-base font-semibold">Capturing class</h2>
      <button type="button" class="text-small text-subtle hover:text-ink" @click="emit('edit')">Edit classes</button>
    </header>

    <ul role="radiogroup" aria-labelledby="class-heading">
      <li v-for="cls in classes" :key="cls.id">
        <button
          type="button"
          role="radio"
          :aria-checked="cls.id === projects.activeClassId"
          class="grid h-[42px] w-full grid-cols-[minmax(0,1fr)_auto] items-center gap-3 border-b border-rule text-left transition-colors"
          :class="cls.id === projects.activeClassId ? 'text-ink' : 'text-subtle hover:text-ink'"
          @click="projects.selectClass(cls.id)"
        >
          <span class="min-w-0 truncate">
            <span :class="cls.id === projects.activeClassId && 'selected-line font-medium'">{{ cls.name }}</span>
          </span>
          <span class="num">{{ formatCount(cls.count) }}</span>
        </button>
      </li>
    </ul>

    <footer class="mt-3 flex items-center justify-between text-small text-subtle">
      <span class="flex items-center gap-1.5"><Kbd>←</Kbd><Kbd>→</Kbd> switch class</span>
      <span class="num">{{ plural(total, 'image') }}</span>
    </footer>
  </section>
</template>
