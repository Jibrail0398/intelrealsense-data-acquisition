<script setup lang="ts">
import { computed, ref } from 'vue'
import { PhPlus, PhSpinnerGap } from '@phosphor-icons/vue'

import { useDatasetStore } from '@/stores/datasetStore'
import { useCaptureStore } from '@/stores/captureStore'

const dataset = useDatasetStore()
const capture = useCaptureStore()

const creating = ref(false)
const newName = ref('')

const options = computed(() =>
  dataset.labels.map((l) => ({ value: l.id, label: l.name })),
)

function startCreate() {
  creating.value = true
  newName.value = ''
}

function confirmCreate() {
  const name = newName.value
  creating.value = false
  if (name.trim()) void dataset.createLabel(name)
}

function cancelCreate() {
  creating.value = false
  newName.value = ''
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <span class="flex items-center justify-between">
      <span class="text-xs font-medium uppercase tracking-wide text-zinc-500">Label</span>
      <span
        v-if="dataset.selectedLabel"
        class="rounded-full bg-blue-50 px-2 py-0.5 font-mono text-[11px] font-medium text-blue-700 ring-1 ring-inset ring-blue-200"
      >
        {{ dataset.selectedLabel.name }}
      </span>
    </span>

    <div v-if="dataset.loadingLabels" class="skeleton h-[38px] w-full" />

    <div v-else-if="creating" class="flex gap-1.5">
      <input
        v-model="newName"
        type="text"
        placeholder="New label name"
        class="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm transition-all duration-300 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600/15"
        autofocus
        @keydown.enter.prevent="confirmCreate"
        @keydown.esc="cancelCreate"
      />
      <button
        class="shrink-0 rounded-md bg-accent px-3 py-2 text-sm font-medium text-white transition-all duration-300 hover:bg-accent-hover active:scale-95 disabled:opacity-60"
        :disabled="dataset.creatingLabel"
        @click="confirmCreate"
      >
        <SpinnerGap v-if="dataset.creatingLabel" class="h-4 w-4 animate-spin" />
        <Plus v-else class="h-4 w-4" weight="bold" />
      </button>
    </div>

    <template v-else>
      <select
        :value="dataset.selectedLabelId ?? ''"
        :disabled="capture.isCapturing"
        class="w-full appearance-none rounded-md border border-zinc-300 bg-white px-3 py-2 pr-8 text-sm transition-all duration-300 hover:border-zinc-400 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600/15 disabled:cursor-not-allowed disabled:bg-zinc-100 disabled:text-zinc-400"
        @change="dataset.selectLabel(($event.target as HTMLSelectElement).value)"
      >
        <option v-for="opt in options" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>

      <button
        type="button"
        :disabled="capture.isCapturing || !dataset.selectedDatasetId"
        class="flex items-center gap-1 self-start rounded-md border border-dashed border-zinc-300 px-2.5 py-1.5 text-xs font-medium text-zinc-500 transition-all duration-300 hover:border-blue-400 hover:text-blue-700 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
        @click="startCreate"
      >
        <Plus class="h-3.5 w-3.5" weight="bold" />
        New Label
      </button>
      <p v-if="capture.isCapturing" class="text-xs text-amber-700">
        Labels are locked during capture.
      </p>
    </template>
  </div>
</template>
