<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { Slider } from '@/components/ui/slider'

// A slider with its value printed, committing on release (not on every pixel).
const props = defineProps<{
  label: string
  modelValue: number
  min: number
  max: number
  step: number
  unit?: string
  digits?: number
  disabled?: boolean
  description?: string
}>()
const emit = defineEmits<{ commit: [value: number] }>()

const local = ref([props.modelValue])
watch(() => props.modelValue, (v) => (local.value = [v]))

const digits = computed(() => props.digits ?? (props.step < 1 ? Math.min(4, String(props.step).split('.')[1]?.length ?? 2) : 0))
const shown = computed(() => (local.value[0] ?? props.modelValue).toFixed(digits.value))
const id = `range-${Math.random().toString(36).slice(2, 8)}`
</script>

<template>
  <div class="grid gap-2 py-2.5">
    <div class="flex items-baseline justify-between gap-3">
      <label :id="id" class="min-w-0 truncate" :title="description">{{ label }}</label>
      <span class="num shrink-0">{{ shown }}<span v-if="unit" class="text-subtle"> {{ unit }}</span></span>
    </div>
    <Slider
      v-model="local"
      :min="min"
      :max="max"
      :step="step"
      :disabled="disabled"
      :aria-labelledby="id"
      @value-commit="(v: number[]) => emit('commit', v[0]!)"
    />
  </div>
</template>
