<script setup lang="ts">
defineProps<{ title: string }>()
</script>

<template>
  <header class="mb-6 flex flex-wrap items-start justify-between gap-x-6 gap-y-3 lg:flex-nowrap">
    <div class="min-w-0 flex-1 basis-[320px]">
      <h1 class="truncate text-title leading-8 font-semibold tracking-[-0.01em]">{{ title }}</h1>
      <div v-if="$slots.subline" class="mt-1 text-subtle"><slot name="subline" /></div>
    </div>
    <div v-if="$slots.actions" class="flex flex-wrap items-center gap-2 lg:shrink-0"><slot name="actions" /></div>
  </header>
</template>
