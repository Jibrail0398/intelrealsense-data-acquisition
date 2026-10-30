<script setup lang="ts">
import { computed } from 'vue'

import SavedStamp from '@/components/common/SavedStamp.vue'
import SettingsRow from '@/components/common/SettingsRow.vue'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useAutoSave } from '@/composables/useAutoSave'
import { useCameraStore } from '@/stores/camera'
import type { FilterConfig } from '@/types'

import RangeField from './RangeField.vue'
import SwitchField from './SwitchField.vue'

const camera = useCameraStore()
const save = useAutoSave()
const f = computed(() => camera.config?.filters)
const aligned = computed(() => camera.config?.align_to_color ?? false)

const HOLE_MODES = [
  { value: 0, label: 'Fill from left' },
  { value: 1, label: 'Farthest from around' },
  { value: 2, label: 'Nearest from around' },
]
const PERSISTENCE = [
  'Disabled', 'Valid in 8/8', 'Valid in 2/last 3', 'Valid in 2/last 4', 'Valid in 2/8',
  'Valid in 1/last 2', 'Valid in 1/last 5', 'Valid in 1/8', 'Always on',
]

function patch<K extends keyof FilterConfig>(key: K, value: Partial<FilterConfig[K]> | FilterConfig[K]) {
  if (!f.value) return
  const current = f.value[key]
  const next = typeof current === 'object' ? { ...current, ...(value as object) } : value
  void save.run(() => camera.updateConfig({ filters: { ...f.value!, [key]: next } }))
}
</script>

<template>
  <SettingsRow
    title="Depth post-processing"
    description="librealsense filters, applied in Intel's order before depth is previewed and saved."
  >
    <template #aside><SavedStamp :state="save.state.value" :error="save.error.value" /></template>

    <div v-if="f" class="grid gap-x-8 gap-y-2 lg:grid-cols-2">
      <div>
        <SwitchField
          label="Threshold"
          description="Drop depth outside a distance band."
          :model-value="f.threshold.enabled"
          @update:model-value="(v) => patch('threshold', { enabled: v })"
        />
        <template v-if="f.threshold.enabled">
          <RangeField label="Nearest" :model-value="f.threshold.min_distance" :min="0" :max="Math.max(0.1, f.threshold.max_distance - 0.05)" :step="0.05" unit="m" @commit="(v) => patch('threshold', { min_distance: v })" />
          <RangeField label="Farthest" :model-value="f.threshold.max_distance" :min="f.threshold.min_distance + 0.05" :max="10" :step="0.05" unit="m" @commit="(v) => patch('threshold', { max_distance: v })" />
        </template>
      </div>

      <div>
        <SwitchField
          label="Decimation"
          description="Downsample depth by a factor; smoother, smaller."
          :model-value="f.decimation.enabled"
          :disabled="aligned"
          disabled-reason="Unavailable while depth is aligned to RGB."
          @update:model-value="(v) => patch('decimation', { enabled: v })"
        />
        <RangeField v-if="f.decimation.enabled" label="Factor" :model-value="f.decimation.magnitude" :min="2" :max="8" :step="1" @commit="(v) => patch('decimation', { magnitude: v })" />
      </div>

      <div>
        <SwitchField
          label="Spatial"
          description="Edge-preserving smoothing within one frame."
          :model-value="f.spatial.enabled"
          @update:model-value="(v) => patch('spatial', { enabled: v })"
        />
        <template v-if="f.spatial.enabled">
          <RangeField label="Passes" :model-value="f.spatial.magnitude" :min="1" :max="5" :step="1" @commit="(v) => patch('spatial', { magnitude: v })" />
          <RangeField label="Smooth alpha" :model-value="f.spatial.smooth_alpha" :min="0.25" :max="1" :step="0.05" @commit="(v) => patch('spatial', { smooth_alpha: v })" />
          <RangeField label="Smooth delta" :model-value="f.spatial.smooth_delta" :min="1" :max="50" :step="1" @commit="(v) => patch('spatial', { smooth_delta: v })" />
          <RangeField label="Hole filling" :model-value="f.spatial.holes_fill" :min="0" :max="5" :step="1" @commit="(v) => patch('spatial', { holes_fill: v })" />
        </template>
      </div>

      <div>
        <SwitchField
          label="Temporal"
          description="Average each pixel over recent frames; best for a still subject."
          :model-value="f.temporal.enabled"
          @update:model-value="(v) => patch('temporal', { enabled: v })"
        />
        <template v-if="f.temporal.enabled">
          <RangeField label="Smooth alpha" :model-value="f.temporal.smooth_alpha" :min="0" :max="1" :step="0.05" @commit="(v) => patch('temporal', { smooth_alpha: v })" />
          <RangeField label="Smooth delta" :model-value="f.temporal.smooth_delta" :min="1" :max="100" :step="1" @commit="(v) => patch('temporal', { smooth_delta: v })" />
          <div class="flex items-center justify-between gap-4 py-2">
            <span>Persistence</span>
            <Select :model-value="String(f.temporal.persistence)" @update:model-value="(v) => patch('temporal', { persistence: Number(v) })">
              <SelectTrigger class="h-[34px] w-[180px]" aria-label="Persistence"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem v-for="(label, i) in PERSISTENCE" :key="i" :value="String(i)">{{ label }}</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </template>
      </div>

      <div>
        <SwitchField
          label="Hole filling"
          description="Fill missing depth from neighbouring pixels."
          :model-value="f.hole_filling.enabled"
          @update:model-value="(v) => patch('hole_filling', { enabled: v })"
        />
        <div v-if="f.hole_filling.enabled" class="flex items-center justify-between gap-4 py-2">
          <span>Mode</span>
          <Select :model-value="String(f.hole_filling.mode)" @update:model-value="(v) => patch('hole_filling', { mode: Number(v) })">
            <SelectTrigger class="h-[34px] w-[200px]" aria-label="Hole filling mode"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem v-for="m in HOLE_MODES" :key="m.value" :value="String(m.value)">{{ m.label }}</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div>
        <SwitchField
          label="Filter in disparity space"
          description="Run spatial and temporal filters on disparity; Intel's recommended setting."
          :model-value="f.disparity_domain"
          @update:model-value="(v) => patch('disparity_domain', v)"
        />
      </div>
    </div>
  </SettingsRow>
</template>
