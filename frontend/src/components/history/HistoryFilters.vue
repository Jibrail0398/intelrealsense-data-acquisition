<script setup lang="ts">
import { Search } from '@lucide/vue'
import { computed } from 'vue'

import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import type { RangePreset } from '@/stores/history'
import { useHistoryStore } from '@/stores/history'
import { useProjectStore } from '@/stores/projects'

const emit = defineEmits<{ change: [] }>()
const history = useHistoryStore()
const projects = useProjectStore()

const ALL = 'all'
const ranges: { value: RangePreset; label: string }[] = [
  { value: 'today', label: 'Today' },
  { value: '7d', label: '7 days' },
  { value: '30d', label: '30 days' },
  { value: 'all', label: 'All time' },
  { value: 'custom', label: 'Custom' },
]

const classOptions = computed(() => {
  const source = history.filters.projectId
    ? projects.projects.filter((p) => p.id === history.filters.projectId)
    : projects.projects
  return [...new Set(source.flatMap((p) => p.classes.map((c) => c.name)))].sort()
})

const projectValue = computed({
  get: () => (history.filters.projectId ? String(history.filters.projectId) : ALL),
  set: (v: string) => {
    history.filters.projectId = v === ALL ? null : Number(v)
    history.filters.className = null
    emit('change')
  },
})

const classValue = computed({
  get: () => history.filters.className ?? ALL,
  set: (v: string) => {
    history.filters.className = v === ALL ? null : v
    emit('change')
  },
})

function setRange(value: RangePreset) {
  history.filters.range = value
  if (value !== 'custom' || history.filters.from || history.filters.to) emit('change')
}

let searchTimer: number | null = null
function onSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = window.setTimeout(() => emit('change'), 250)
}
</script>

<template>
  <div class="mb-5 grid gap-3">
    <div class="flex flex-wrap items-center gap-x-5 gap-y-3">
      <div role="radiogroup" aria-label="Time range" class="flex flex-wrap items-center gap-x-4 border-b border-border">
        <button
          v-for="r in ranges"
          :key="r.value"
          type="button"
          role="radio"
          :aria-checked="history.filters.range === r.value"
          class="h-9 transition-colors"
          :class="history.filters.range === r.value ? 'selected-line text-ink' : 'text-subtle hover:text-ink'"
          @click="setRange(r.value)"
        >
          {{ r.label }}
        </button>
      </div>

      <div v-if="history.filters.range === 'custom'" class="flex items-center gap-2">
        <Input
          v-model="history.filters.from"
          type="date"
          class="h-[34px] w-[150px]"
          aria-label="From date"
          :max="history.filters.to || undefined"
          @change="emit('change')"
        />
        <span class="text-subtle">to</span>
        <Input
          v-model="history.filters.to"
          type="date"
          class="h-[34px] w-[150px]"
          aria-label="To date"
          :min="history.filters.from || undefined"
          @change="emit('change')"
        />
      </div>
    </div>

    <div class="flex flex-wrap items-center gap-2">
      <Select v-model="projectValue">
        <SelectTrigger class="h-[34px] w-[220px]" aria-label="Project">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem :value="ALL">All projects</SelectItem>
          <SelectItem v-for="p in projects.projects" :key="p.id" :value="String(p.id)">{{ p.name }}</SelectItem>
        </SelectContent>
      </Select>

      <Select v-model="classValue">
        <SelectTrigger class="h-[34px] w-[180px]" aria-label="Class">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem :value="ALL">All classes</SelectItem>
          <SelectItem v-for="c in classOptions" :key="c" :value="c">{{ c }}</SelectItem>
        </SelectContent>
      </Select>

      <div class="relative w-full sm:ml-auto sm:w-[280px]">
        <Search class="pointer-events-none absolute top-1/2 left-3 size-3.5 -translate-y-1/2 text-subtle" />
        <Input
          v-model="history.filters.q"
          class="h-[34px] pl-9"
          placeholder="Search image name"
          aria-label="Search image name"
          @input="onSearch"
        />
      </div>
    </div>
  </div>
</template>
