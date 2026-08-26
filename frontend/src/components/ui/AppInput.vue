<script setup lang="ts">
import type { Component } from 'vue'

const props = withDefaults(
  defineProps<{
    label: string
    modelValue: string | number
    type?: 'text' | 'number'
    unit?: string
    disabled?: boolean
    error?: string
    helper?: string
    min?: number
    max?: number
    icon?: Component
  }>(),
  { type: 'text' },
)

const emit = defineEmits<{ (e: 'update:modelValue', v: string | number): void }>()

function onInput(evt: Event) {
  const raw = (evt.target as HTMLInputElement).value
  emit('update:modelValue', props.type === 'number' ? Number(raw) : raw)
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <label class="text-xs font-medium uppercase tracking-wide text-zinc-500">
      {{ label }}
    </label>
    <div class="relative">
      <span v-if="icon" class="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400">
        <component :is="icon" class="h-4 w-4" />
      </span>
      <input
        :type="type"
        :value="modelValue"
        :min="min"
        :max="max"
        :disabled="disabled"
        class="rounded-md border bg-white py-2 text-sm text-zinc-900 transition-all duration-300 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] hover:border-zinc-400 focus:outline-none focus:ring-2 focus:ring-blue-600/15 disabled:cursor-not-allowed disabled:bg-zinc-100 disabled:text-zinc-400"
        :class="[
          icon ? 'pl-9' : 'pl-3',
          unit ? 'pr-12' : 'pr-3',
          error
            ? 'border-red-400 focus:border-red-500 focus:ring-red-500/15'
            : 'border-zinc-300 focus:border-blue-600',
        ]"
        @input="onInput"
      />
      <span
        v-if="unit"
        class="absolute right-3 top-1/2 -translate-y-1/2 font-mono text-xs text-zinc-400"
      >
        {{ unit }}
      </span>
    </div>
    <p v-if="error" class="text-xs text-red-600">{{ error }}</p>
    <p v-else-if="helper" class="text-xs text-zinc-400">{{ helper }}</p>
  </div>
</template>
