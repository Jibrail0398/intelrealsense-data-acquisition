<script setup lang="ts">
import { X } from '@lucide/vue'
import { ref } from 'vue'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { classNameProblem } from '@/utils/validators'

// Class names typed before the project exists; Enter or comma adds one.
defineProps<{ id?: string; describedBy?: string }>()
const model = defineModel<string[]>({ required: true })
const draft = ref('')
const error = ref<string | null>(null)

function add() {
  const parts = draft.value.split(',').map((p) => p.trim()).filter(Boolean)
  for (const name of parts) {
    const problem = classNameProblem(name, model.value)
    if (problem) {
      error.value = problem
      return
    }
    model.value = [...model.value, name.replace(/\s+/g, ' ')]
  }
  draft.value = ''
  error.value = null
}

function onKey(event: KeyboardEvent) {
  if (event.key === 'Enter' || event.key === ',') {
    event.preventDefault()
    add()
  }
}

function remove(i: number) {
  model.value = model.value.filter((_, j) => j !== i)
}
</script>

<template>
  <div>
    <div class="flex gap-2">
      <Input
        :id="id"
        v-model="draft"
        placeholder="e.g. stunting"
        :aria-describedby="describedBy"
        @keydown="onKey"
      />
      <Button type="button" variant="outline" :disabled="!draft.trim()" @click="add">Add class</Button>
    </div>
    <p v-if="error" class="mt-1.5 text-negative">{{ error }}</p>
    <ul v-if="model.length" class="mt-3 flex flex-wrap gap-2" aria-label="Classes">
      <li
        v-for="(name, i) in model"
        :key="name"
        class="flex h-7 flex-none items-center gap-1 rounded-full bg-raised pr-1 pl-3 whitespace-nowrap"
      >
        {{ name }}
        <button
          type="button"
          class="grid size-5 place-items-center rounded-full text-subtle hover:bg-active hover:text-ink"
          :aria-label="`Remove ${name}`"
          @click="remove(i)"
        >
          <X class="size-3.5" />
        </button>
      </li>
    </ul>
  </div>
</template>
