<script setup lang="ts">
defineProps<{ title: string; description?: string }>()
</script>

<template>
  <!-- Label column beside its panel; stacks on narrow screens. -->
  <section class="grid grid-cols-[minmax(0,1fr)] gap-3 py-6 first:pt-0 lg:grid-cols-[280px_minmax(0,1fr)] lg:gap-6">
    <div>
      <h2 class="text-base font-semibold">{{ title }}</h2>
      <p v-if="description" class="mt-1 text-subtle">{{ description }}</p>
      <div v-if="$slots.aside" class="mt-3"><slot name="aside" /></div>
    </div>
    <div class="min-w-0 rounded-md border border-border bg-surface p-5 shadow-[var(--shadow)]">
      <slot />
    </div>
  </section>
</template>
