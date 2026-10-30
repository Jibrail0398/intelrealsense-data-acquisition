<script setup lang="ts">
import SavedStamp from '@/components/common/SavedStamp.vue'
import SettingsRow from '@/components/common/SettingsRow.vue'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useAutoSave } from '@/composables/useAutoSave'
import { useCameraStore } from '@/stores/camera'
import type { Colormap, PreviewConfig } from '@/types'

import RangeField from './RangeField.vue'

const camera = useCameraStore()
const save = useAutoSave()

const COLORMAPS: { value: Colormap; label: string }[] = [
  { value: 'turbo', label: 'Turbo' },
  { value: 'jet', label: 'Jet' },
  { value: 'inferno', label: 'Inferno' },
  { value: 'viridis', label: 'Viridis' },
  { value: 'bone', label: 'Greyscale' },
]

function patch(value: Partial<PreviewConfig>) {
  if (!camera.config) return
  void save.run(() => camera.updateConfig({ preview: { ...camera.config!.preview, ...value } }))
}
</script>

<template>
  <SettingsRow
    title="Depth preview"
    description="How depth is coloured on screen. Saved files always keep the raw 16-bit values."
  >
    <template #aside><SavedStamp :state="save.state.value" :error="save.error.value" /></template>
    <div v-if="camera.config" class="grid gap-x-8 lg:grid-cols-3">
      <div class="flex items-center justify-between gap-4 py-2 lg:col-span-1">
        <span>Colour map</span>
        <Select :model-value="camera.config.preview.colormap" @update:model-value="(v) => patch({ colormap: v as Colormap })">
          <SelectTrigger class="h-[34px] w-[150px]" aria-label="Colour map"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem v-for="c in COLORMAPS" :key="c.value" :value="c.value">{{ c.label }}</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <RangeField
        label="Near end"
        :model-value="camera.config.preview.min_distance"
        :min="0"
        :max="Math.max(0.1, camera.config.preview.max_distance - 0.1)"
        :step="0.1"
        unit="m"
        @commit="(v) => patch({ min_distance: v })"
      />
      <RangeField
        label="Far end"
        :model-value="camera.config.preview.max_distance"
        :min="camera.config.preview.min_distance + 0.1"
        :max="10"
        :step="0.1"
        unit="m"
        @commit="(v) => patch({ max_distance: v })"
      />
    </div>
  </SettingsRow>
</template>
