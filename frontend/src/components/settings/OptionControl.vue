<script setup lang="ts">
import { computed } from 'vue'

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import type { SensorOption } from '@/types'

import RangeField from './RangeField.vue'
import SwitchField from './SwitchField.vue'

// One pyrealsense2 option, drawn by its kind: on/off, a list of named values, or a range.
const props = defineProps<{ option: SensorOption; disabled?: boolean }>()
const emit = defineEmits<{ change: [value: number] }>()

const choiceValue = computed(() => String(props.option.value))
const unit = computed(() => {
  const n = props.option.name
  if (n.includes('exposure') && !n.startsWith('enable')) return 'µs'
  if (n === 'laser_power') return 'mW'
  if (n === 'white_balance') return 'K'
  if (n.includes('temperature')) return '°C'
  if (n === 'depth_units') return 'm'
  return undefined
})
</script>

<template>
  <div v-if="option.read_only" class="flex items-baseline justify-between gap-3 py-2.5">
    <span class="truncate" :title="option.description">{{ option.label }}</span>
    <span class="num text-subtle">{{ option.value }}<span v-if="unit"> {{ unit }}</span></span>
  </div>

  <SwitchField
    v-else-if="option.kind === 'bool'"
    :label="option.label"
    :model-value="option.value === 1"
    :disabled="disabled"
    @update:model-value="(v) => emit('change', v ? 1 : 0)"
  />

  <div v-else-if="option.kind === 'choice'" class="flex items-center justify-between gap-4 py-2">
    <label class="min-w-0 truncate" :title="option.description">{{ option.label }}</label>
    <Select :model-value="choiceValue" :disabled="disabled" @update:model-value="(v) => emit('change', Number(v))">
      <SelectTrigger class="h-[34px] w-[160px] sm:w-[200px]" :aria-label="option.label">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem v-for="c in option.choices ?? []" :key="c.value" :value="String(c.value)">{{ c.label }}</SelectItem>
      </SelectContent>
    </Select>
  </div>

  <RangeField
    v-else
    :label="option.label"
    :description="option.description"
    :model-value="option.value"
    :min="option.min"
    :max="option.max"
    :step="option.step || 1"
    :unit="unit"
    :disabled="disabled"
    @commit="(v) => emit('change', v)"
  />
</template>
