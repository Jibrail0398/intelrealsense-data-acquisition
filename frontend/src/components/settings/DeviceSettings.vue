<script setup lang="ts">
import { computed, ref } from 'vue'
import { toast } from 'vue-sonner'

import CameraStatusDot from '@/components/common/CameraStatusDot.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import SettingsRow from '@/components/common/SettingsRow.vue'
import { Button } from '@/components/ui/button'
import { errorMessage } from '@/services/api'
import { useCameraStore } from '@/stores/camera'

const camera = useCameraStore()
const resetOpen = ref(false)

const LABELS: Record<string, string> = {
  name: 'Model',
  serial_number: 'Serial number',
  firmware_version: 'Firmware',
  recommended_firmware_version: 'Recommended firmware',
  usb_type: 'USB',
  product_line: 'Product line',
  product_id: 'Product ID',
}
const rows = computed(() =>
  Object.entries(camera.status?.device ?? {}).map(([k, v]) => ({ key: k, label: LABELS[k] ?? k, value: v })),
)
const usbWarning = computed(() => {
  const usb = camera.status?.device?.usb_type
  return usb && usb.startsWith('2') ? 'Connected over USB 2. Use a USB 3 port and cable for full resolution and frame rate.' : null
})

async function act(fn: () => Promise<unknown>, done: string) {
  try {
    await fn()
    toast(done)
  } catch (err) {
    toast.error(errorMessage(err))
  }
}
</script>

<template>
  <SettingsRow title="Device" description="The RealSense camera on USB, read through pyrealsense2. It reconnects by itself when plugged in.">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <p class="flex items-center gap-2 font-medium">
        <CameraStatusDot />
        {{ camera.isConnected ? 'Connected' : camera.status?.message ?? 'Not connected' }}
        <span v-if="camera.status?.backend === 'mock'" class="rounded-sm bg-raised px-1.5 py-0.5 text-small font-normal text-subtle">simulated</span>
      </p>
      <div class="flex gap-2">
        <Button v-if="camera.isConnected" variant="outline" size="sm" @click="act(camera.disconnect, 'Camera disconnected')">Disconnect</Button>
        <Button v-else variant="outline" size="sm" @click="act(camera.connect, 'Connecting…')">Connect</Button>
        <Button variant="outline" size="sm" :disabled="!camera.isConnected" @click="resetOpen = true">Hardware reset</Button>
      </div>
    </div>

    <dl v-if="rows.length" class="mt-4 grid grid-cols-[120px_minmax(0,1fr)] gap-y-1.5 sm:grid-cols-[160px_minmax(0,1fr)]">
      <template v-for="row in rows" :key="row.key">
        <dt class="text-subtle">{{ row.label }}</dt>
        <dd class="truncate num">{{ row.value }}</dd>
      </template>
      <dt class="text-subtle">Measured rate</dt>
      <dd class="num">{{ camera.status?.fps.toFixed(1) }} fps</dd>
    </dl>
    <p v-if="usbWarning" class="mt-3 text-[var(--pill-warning-ink)]">{{ usbWarning }}</p>

    <ConfirmDialog
      v-model:open="resetOpen"
      title="Reset the camera?"
      description="The camera reboots (about 5 seconds) and restores its factory option values. Saved options are applied again when it reconnects."
      confirm-label="Reset camera"
      @confirm="act(camera.hardwareReset, 'Camera is resetting')"
    />
  </SettingsRow>
</template>
