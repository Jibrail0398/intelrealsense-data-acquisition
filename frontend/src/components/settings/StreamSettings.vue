<script setup lang="ts">
import { computed } from 'vue'

import SavedStamp from '@/components/common/SavedStamp.vue'
import SettingsRow from '@/components/common/SettingsRow.vue'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useAutoSave } from '@/composables/useAutoSave'
import { useCameraStore } from '@/stores/camera'
import type { ResolutionOption, StreamProfile } from '@/types'

import SwitchField from './SwitchField.vue'

const camera = useCameraStore()
const save = useAutoSave()

const streams = computed(() => [
  { key: 'color' as const, label: 'RGB', options: camera.capabilities?.color ?? [] },
  { key: 'depth' as const, label: 'Depth', options: camera.capabilities?.depth ?? [] },
])

const resKey = (p: { width: number; height: number }) => `${p.width}x${p.height}`

function ratesFor(options: ResolutionOption[], profile: StreamProfile): number[] {
  return options.find((o) => resKey(o) === resKey(profile))?.fps ?? [profile.fps]
}

function setResolution(key: 'color' | 'depth', options: ResolutionOption[], value: string) {
  const res = options.find((o) => resKey(o) === value)
  const current = camera.config?.[key]
  if (!res || !current) return
  const fps = res.fps.includes(current.fps) ? current.fps : res.fps[res.fps.length - 1]!
  void save.run(() => camera.updateConfig({ [key]: { width: res.width, height: res.height, fps } }))
}

function setFps(key: 'color' | 'depth', value: string) {
  const current = camera.config?.[key]
  if (!current) return
  void save.run(() => camera.updateConfig({ [key]: { ...current, fps: Number(value) } }))
}

function setAlign(value: boolean) {
  void save.run(() => camera.updateConfig({ align_to_color: value }))
}

const decimationOn = computed(() => camera.config?.filters.decimation.enabled ?? false)
</script>

<template>
  <SettingsRow
    title="Streams"
    description="Resolution and frame rate of each sensor. Changing them restarts the camera for a second."
  >
    <template #aside><SavedStamp :state="save.state.value" :error="save.error.value" /></template>

    <div v-if="camera.config" class="grid gap-4">
      <div v-for="s in streams" :key="s.key" class="grid grid-cols-[minmax(0,1fr)] items-center gap-2 sm:grid-cols-[80px_minmax(0,1fr)_120px] sm:gap-3">
        <span>{{ s.label }}</span>
        <Select
          :model-value="resKey(camera.config[s.key])"
          :disabled="!s.options.length"
          @update:model-value="(v) => setResolution(s.key, s.options, String(v))"
        >
          <SelectTrigger class="h-[34px] w-full" :aria-label="`${s.label} resolution`"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem v-for="o in s.options" :key="resKey(o)" :value="resKey(o)">{{ o.width }} × {{ o.height }}</SelectItem>
          </SelectContent>
        </Select>
        <Select
          :model-value="String(camera.config[s.key].fps)"
          :disabled="!s.options.length"
          @update:model-value="(v) => setFps(s.key, String(v))"
        >
          <SelectTrigger class="h-[34px] w-full" :aria-label="`${s.label} frame rate`"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem v-for="f in ratesFor(s.options, camera.config[s.key])" :key="f" :value="String(f)">{{ f }} fps</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <p v-if="!camera.capabilities" class="text-subtle">Connect the camera to list the resolutions it supports.</p>

      <SwitchField
        label="Align depth to RGB"
        description="Depth is re-projected onto the RGB image, so pixel (x, y) is the same point in both files."
        :model-value="camera.config.align_to_color"
        :disabled="decimationOn"
        disabled-reason="Turn off the decimation filter first; it shrinks depth below the RGB size."
        @update:model-value="setAlign"
      />
    </div>
  </SettingsRow>
</template>
