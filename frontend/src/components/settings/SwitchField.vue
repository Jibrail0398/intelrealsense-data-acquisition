<script setup lang="ts">
import { Switch } from '@/components/ui/switch'

defineProps<{ label: string; description?: string; modelValue: boolean; disabled?: boolean; disabledReason?: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()
const id = `switch-${Math.random().toString(36).slice(2, 8)}`
</script>

<template>
  <div class="flex items-start justify-between gap-4 py-2.5">
    <div class="min-w-0">
      <label :for="id" class="block">{{ label }}</label>
      <p v-if="description" class="text-small text-subtle">{{ description }}</p>
      <p v-if="disabled && disabledReason" class="text-small text-subtle">{{ disabledReason }}</p>
    </div>
    <Switch
      :id="id"
      class="mt-0.5"
      :model-value="modelValue"
      :disabled="disabled"
      @update:model-value="(v: boolean) => emit('update:modelValue', v)"
    />
  </div>
</template>
