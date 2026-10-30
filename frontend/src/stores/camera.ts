import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { errorMessage } from '@/services/api'
import { cameraService } from '@/services/cameraService'
import { eventSocket } from '@/services/eventSocket'
import type {
  CameraConfig,
  CameraConfigUpdate,
  CameraStatus,
  SensorOptions,
  StreamCapabilities,
} from '@/types'

export const useCameraStore = defineStore('camera', () => {
  const status = ref<CameraStatus | null>(null)
  const backendOnline = ref(true)
  const config = ref<CameraConfig | null>(null)
  const capabilities = ref<StreamCapabilities | null>(null)
  const sensors = ref<SensorOptions[]>([])
  const sensorsError = ref<string | null>(null)
  // Bumped whenever the stream (re)starts, so <img> elements reopen the MJPEG feed.
  const streamNonce = ref(Date.now())

  const isConnected = computed(() => status.value?.status === 'connected')
  const deviceName = computed(() => status.value?.device?.name ?? null)

  let started = false

  function applyStatus(next: CameraStatus) {
    const wasConnected = isConnected.value
    status.value = next
    if (next.status === 'connected' && !wasConnected) streamNonce.value = Date.now()
  }

  async function init() {
    if (started) return
    started = true
    eventSocket.on('camera.status', applyStatus)
    eventSocket.on('camera.config', (c: CameraConfig) => (config.value = c))
    eventSocket.onOpenChange = (open) => {
      backendOnline.value = open
      if (open) void refreshStatus()
    }
    eventSocket.start()
    await Promise.allSettled([refreshStatus(), loadConfig()])
  }

  async function refreshStatus() {
    try {
      applyStatus(await cameraService.status())
      backendOnline.value = true
    } catch {
      backendOnline.value = false
    }
  }

  async function loadConfig() {
    config.value = await cameraService.config()
  }

  async function loadCapabilities() {
    capabilities.value = await cameraService.capabilities()
  }

  async function loadSensors() {
    try {
      sensors.value = await cameraService.options()
      sensorsError.value = null
    } catch (err) {
      sensors.value = []
      sensorsError.value = errorMessage(err)
    }
  }

  async function updateConfig(update: CameraConfigUpdate) {
    config.value = await cameraService.updateConfig(update)
    return config.value
  }

  async function setOption(sensor: string, option: string, value: number) {
    sensors.value = await cameraService.setOption(sensor, option, value)
  }

  async function resetOptions() {
    sensors.value = await cameraService.resetOptions()
  }

  async function connect() {
    applyStatus(await cameraService.connect())
  }

  async function disconnect() {
    applyStatus(await cameraService.disconnect())
  }

  async function hardwareReset() {
    applyStatus(await cameraService.hardwareReset())
  }

  return {
    status, backendOnline, config, capabilities, sensors, sensorsError, streamNonce,
    isConnected, deviceName,
    init, refreshStatus, loadConfig, loadCapabilities, loadSensors, updateConfig,
    setOption, resetOptions, connect, disconnect, hardwareReset,
  }
})
