<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useDatasetStore } from '@/stores/datasetStore'
import AppSelect from '@/components/ui/AppSelect.vue'

const dataset = useDatasetStore()

onMounted(() => {
  if (!dataset.selectedDatasetId && dataset.datasets.length > 0) {
    void dataset.selectDataset(dataset.datasets[0]!.id)
  }
})

const options = computed(() =>
  dataset.datasets.map((d) => ({ value: d.id, label: d.name })),
)
</script>

<template>
  <div v-if="dataset.loadingDatasets" class="flex flex-col gap-2">
    <span class="text-xs font-medium uppercase tracking-wide text-zinc-500">Dataset</span>
    <div class="skeleton h-[38px] w-full" />
  </div>

  <div
    v-else-if="options.length === 0"
    class="flex flex-col gap-2"
  >
    <span class="text-xs font-medium uppercase tracking-wide text-zinc-500">Dataset</span>
    <div class="rounded-md border border-dashed border-zinc-300 px-3 py-3 text-center text-xs text-zinc-400">
      No datasets registered on the backend yet.
    </div>
  </div>

  <AppSelect
    v-else
    label="Dataset"
    :model-value="dataset.selectedDatasetId ?? ''"
    :options="options"
    helper="Captures are filed under the selected dataset."
    @update:model-value="(v) => dataset.selectDataset(v)"
  />
</template>
