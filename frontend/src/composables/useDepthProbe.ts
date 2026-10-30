import { ref } from 'vue'

import { cameraService } from '@/services/cameraService'

/** Reads the distance under the pointer on the depth preview, throttled to one request in flight. */
export function useDepthProbe() {
  const reading = ref<{ x: number; y: number; metres: number } | null>(null)
  let inFlight = false

  async function probe(event: MouseEvent, frameWidth: number, frameHeight: number) {
    if (inFlight) return
    const el = event.currentTarget as HTMLElement
    const rect = el.getBoundingClientRect()
    const x = Math.floor(((event.clientX - rect.left) / rect.width) * frameWidth)
    const y = Math.floor(((event.clientY - rect.top) / rect.height) * frameHeight)
    if (x < 0 || y < 0 || x >= frameWidth || y >= frameHeight) return
    inFlight = true
    try {
      const sample = await cameraService.depthAt(x, y)
      reading.value = { x, y, metres: sample.distance_m }
    } catch {
      reading.value = null
    } finally {
      inFlight = false
    }
  }

  function clear() {
    reading.value = null
  }

  return { reading, probe, clear }
}
