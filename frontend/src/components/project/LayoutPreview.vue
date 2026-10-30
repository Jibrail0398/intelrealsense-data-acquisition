<script setup lang="ts">
import { computed } from 'vue'

import { useProjectStore } from '@/stores/projects'
import type { FormatKey } from '@/types'

// Shows the folder tree the project will write, before anything is captured.
const props = defineProps<{ destination: string; formats: FormatKey[]; classes: string[] }>()
const projects = useProjectStore()

const rows = computed(() => {
  const fmts = projects.formats.filter((f) => props.formats.includes(f.key))
  const classes = props.classes.length ? props.classes : ['class']
  const lines: { depth: number; text: string }[] = []
  for (const f of fmts) {
    lines.push({ depth: 0, text: `${f.folder}/` })
    for (const c of classes) {
      lines.push({ depth: 1, text: `${c}/` })
      lines.push({ depth: 2, text: `${c}-0001.${f.ext}` })
    }
  }
  return lines
})
</script>

<template>
  <div class="rounded-sm bg-ground px-3 py-2.5 font-mono text-small leading-6" aria-label="Folder layout preview">
    <p class="truncate text-subtle" :title="destination">{{ destination || 'destination folder' }}/</p>
    <p v-if="!rows.length" class="text-faint">Choose at least one output format.</p>
    <p
      v-for="(row, i) in rows"
      :key="i"
      class="truncate"
      :class="row.depth === 2 ? 'text-subtle' : 'text-ink'"
      :style="{ paddingLeft: `${(row.depth + 1) * 16}px` }"
    >
      {{ row.text }}
    </p>
  </div>
</template>
