<script setup lang="ts">
import { ref } from 'vue'

import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import SavedStamp from '@/components/common/SavedStamp.vue'
import SettingsRow from '@/components/common/SettingsRow.vue'
import { Button } from '@/components/ui/button'
import { useAutoSave } from '@/composables/useAutoSave'
import { useCameraStore } from '@/stores/camera'
import type { SensorOptions } from '@/types'

import OptionControl from './OptionControl.vue'

const camera = useCameraStore()
const save = useAutoSave()
const resetOpen = ref(false)

const DESCRIPTIONS: Record<string, string> = {
  stereo_module: 'Depth: projector, exposure and the preset that tunes the depth algorithm.',
  rgb_camera: 'Colour: exposure, white balance and the image controls of the RGB sensor.',
  motion_module: 'IMU: accelerometer and gyroscope (D435i / D455).',
}

function change(sensor: SensorOptions, name: string, value: number) {
  void save.run(() => camera.setOption(sensor.key, name, value))
}
</script>

<template>
  <SettingsRow
    v-for="sensor in camera.sensors"
    :key="sensor.key"
    :title="sensor.name"
    :description="DESCRIPTIONS[sensor.key] ?? 'Options reported by this sensor.'"
  >
    <template #aside>
      <p class="text-small text-subtle">Every option this sensor reports through pyrealsense2. Changes save at once and return after a reconnect.</p>
    </template>
    <div class="grid gap-x-8 lg:grid-cols-2">
      <OptionControl
        v-for="opt in sensor.options"
        :key="opt.name"
        :option="opt"
        @change="(v) => change(sensor, opt.name, v)"
      />
    </div>
  </SettingsRow>

  <SettingsRow
    v-if="camera.sensors.length"
    title="Sensor defaults"
    description="Put every sensor option above back to its factory value."
  >
    <div class="flex items-center justify-between gap-3">
      <SavedStamp :state="save.state.value" :error="save.error.value" />
      <Button variant="outline" @click="resetOpen = true">Reset sensor options</Button>
    </div>
    <ConfirmDialog
      v-model:open="resetOpen"
      title="Reset all sensor options?"
      description="Exposure, gain, white balance, laser power and the rest return to the camera's defaults."
      confirm-label="Reset options"
      @confirm="save.run(camera.resetOptions)"
    />
  </SettingsRow>

  <SettingsRow v-else title="Sensor options" description="Exposure, gain, laser power, white balance and more.">
    <p class="text-subtle">{{ camera.sensorsError ?? 'Connect the camera to read its sensor options.' }}</p>
  </SettingsRow>
</template>
