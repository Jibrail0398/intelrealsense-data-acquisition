<script setup lang="ts">
import { computed } from 'vue'

import { Checkbox } from '@/components/ui/checkbox'
import { useProjectStore } from '@/stores/projects'
import type { FormatKey } from '@/types'

const model = defineModel<FormatKey[]>({ required: true })
defineProps<{ disabled?: boolean }>()

const projects = useProjectStore()
const groups = computed(() => [
  { title: 'RGB', items: projects.formats.filter((f) => f.kind === 'rgb') },
  { title: 'Depth', items: projects.formats.filter((f) => f.kind === 'depth') },
])

function toggle(key: FormatKey, on: boolean | 'indeterminate') {
  const next = new Set(model.value)
  if (on === true) next.add(key)
  else next.delete(key)
  // keep the registry order
  model.value = projects.formats.map((f) => f.key).filter((k) => next.has(k))
}
</script>

<template>
  <div class="grid gap-4 sm:grid-cols-2">
    <fieldset v-for="group in groups" :key="group.title" class="min-w-0">
      <legend class="mb-2 text-subtle">{{ group.title }}</legend>
      <label
        v-for="fmt in group.items"
        :key="fmt.key"
        class="flex cursor-pointer items-start gap-3 rounded-sm py-1.5"
      >
        <Checkbox
          class="mt-0.5"
          :model-value="model.includes(fmt.key)"
          :disabled="disabled"
          @update:model-value="(v) => toggle(fmt.key, v)"
        />
        <span class="min-w-0">
          <span class="block">{{ fmt.label }} <span class="font-mono text-small text-faint">.{{ fmt.ext }}</span></span>
          <span class="block text-small text-subtle">{{ fmt.description }}</span>
        </span>
      </label>
    </fieldset>
  </div>
</template>
