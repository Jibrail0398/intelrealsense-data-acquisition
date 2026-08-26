<script setup lang="ts">
defineProps<{
  label: string
  modelValue: string | number
  options: { value: string | number; label: string }[]
  disabled?: boolean
  helper?: string
}>()

const emit = defineEmits<{ (e: 'update:modelValue', v: string): void }>()
</script>

<template>
  <div class="flex flex-col gap-2">
    <label class="text-xs font-medium uppercase tracking-wide text-zinc-500">
      {{ label }}
    </label>
    <div class="relative">
      <select
        :value="modelValue"
        :disabled="disabled"
        class="w-full appearance-none rounded-md border border-zinc-300 bg-white px-3 py-2 pr-8 text-sm text-zinc-900 transition-all duration-300 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] hover:border-zinc-400 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600/15 disabled:cursor-not-allowed disabled:bg-zinc-100 disabled:text-zinc-400"
        @change="emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
      >
        <option v-for="opt in options" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>
      <svg
        class="pointer-events-none absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400"
        viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"
      >
        <path d="M4 6l4 4 4-4" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </div>
    <p v-if="helper" class="text-xs text-zinc-400">{{ helper }}</p>
  </div>
</template>
