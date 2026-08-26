import type {
  CameraOptionsPayload,
  CameraSettings,
  CameraStatus,
  CaptureMode,
  DatasetInfo,
  LabelInfo,
} from '@/types'

export type MockEvent =
  | 'camera.status'
  | 'camera.frame'
  | 'capture.started'
  | 'capture.progress'
  | 'capture.completed'
  | 'capture.failed'
  | 'storage.updated'
  | 'dataset.updated'
  | 'depth.invalid'

type Listener = (payload: unknown) => void

interface CaptureSession {
  mode: CaptureMode
  remaining: number | null
  intervalMs: number
  captured: number
  datasetId: string
  labelId: string
}

const RGB_W = 320
const RGB_H = 240

function makeCanvas(): { canvas: HTMLCanvasElement; ctx: CanvasRenderingContext2D } | null {
  if (typeof document === 'undefined') return null
  const canvas = document.createElement('canvas')
  canvas.width = RGB_W
  canvas.height = RGB_H
  const ctx = canvas.getContext('2d')
  return ctx ? { canvas, ctx } : null
}

function drawScene(ctx: CanvasRenderingContext2D, t: number, depth: boolean) {
  const w = RGB_W
  const h = RGB_H
  const sway = Math.sin(t / 900) * 4

  ctx.fillStyle = depth ? '#b9b9b9' : '#cfcac2'
  ctx.fillRect(0, 0, w, h)

  ctx.fillStyle = depth ? '#a3a3a3' : '#b8b2a7'
  ctx.fillRect(0, h * 0.68, w, h * 0.32)

  const cx = w / 2 + sway
  const baseY = h * 0.78

  ctx.save()
  ctx.translate(cx, baseY)
  ctx.fillStyle = depth ? '#8f8f8f' : '#9a5f3f'
  ctx.beginPath()
  ctx.moveTo(-26, 0)
  ctx.lineTo(26, 0)
  ctx.lineTo(18, -44)
  ctx.lineTo(-18, -44)
  ctx.closePath()
  ctx.fill()

  const leafAngles = [-1.15, -0.6, 0, 0.6, 1.15]
  for (let i = 0; i < leafAngles.length; i++) {
    const a = leafAngles[i]! + Math.sin(t / 1100 + i) * 0.05
    const len = 62 + (i % 2) * 14
    ctx.save()
    ctx.rotate(a)
    const grad = ctx.createLinearGradient(0, -44, 0, -44 - len)
    if (depth) {
      grad.addColorStop(0, '#565656')
      grad.addColorStop(1, '#6e6e6e')
    } else {
      grad.addColorStop(0, '#3f6f3a')
      grad.addColorStop(1, '#5d8f4e')
    }
    ctx.fillStyle = grad
    ctx.beginPath()
    ctx.ellipse(0, -44 - len / 2, len * 0.22, len / 2, 0, 0, Math.PI * 2)
    ctx.fill()
    ctx.restore()
  }
  ctx.restore()
}

class MockEngine {
  private listeners = new Map<MockEvent, Set<Listener>>()
  private frameTimer: ReturnType<typeof setInterval> | null = null
  private captureTimer: ReturnType<typeof setInterval> | null = null
  private rgbCanvasCtx: CanvasRenderingContext2D | null = null
  private lastRgbDataUrl = ''
  private t = 0
  private session: CaptureSession | null = null

  cameraStatus: CameraStatus = 'connecting'
  streamRestarting = false

  settings: CameraSettings = {
    rgbResolution: '640x480',
    depthResolution: '640x480',
    fps: 30,
    exposure: 'auto',
    whiteBalance: 'auto',
  }

  options: CameraOptionsPayload = {
    rgbResolutions: ['1280x720', '640x480', '480x270'],
    depthResolutions: ['848x480', '640x480', '320x240'],
    fpsOptions: [6, 15, 30],
    exposureModes: ['auto', 'manual'],
    whiteBalanceModes: ['auto', '3200 K', '4500 K', '6500 K'],
  }

  datasets: DatasetInfo[] = [
    { id: 'ds-rice', name: 'Rice Disease' },
    { id: 'ds-leaf', name: 'Leaf Morphology' },
  ]

  labels: LabelInfo[] = [
    { id: 'lb-brownspot', name: 'Brownspot', datasetId: 'ds-rice' },
    { id: 'lb-blight', name: 'Bacterialblight', datasetId: 'ds-rice' },
    { id: 'lb-leafsmut', name: 'Leafsmut', datasetId: 'ds-rice' },
    { id: 'lb-obovate', name: 'Obovate', datasetId: 'ds-leaf' },
    { id: 'lb-lanceolate', name: 'Lanceolate', datasetId: 'ds-leaf' },
  ]

  statistics: Record<string, Record<string, number>> = {
    'ds-rice': { 'lb-brownspot': 127, 'lb-blight': 132, 'lb-leafsmut': 119 },
    'ds-leaf': { 'lb-obovate': 64, 'lb-lanceolate': 58 },
  }

  recent: {
    id: string
    datasetId: string
    labelId: string
    labelName: string
    rgbFilename: string
    depthFilename: string
    pairOk: boolean
    timestamp: number
  }[] = []

  storage = {
    path: '/home/research/datasets/realsense',
    availableGb: 350.4,
    usedByDatasetGb: 1.24,
    lowStorageThresholdGb: 20,
  }

  private browseIndex = 0
  private browseCandidates = [
    '/home/research/datasets/realsense',
    '/media/research/ssd-01/rgbd-captures',
    '/mnt/data/stunting-collection',
  ]

  on(event: MockEvent, cb: Listener): () => void {
    if (!this.listeners.has(event)) this.listeners.set(event, new Set())
    this.listeners.get(event)!.add(cb)
    return () => this.listeners.get(event)?.delete(cb)
  }

  emit(event: MockEvent, payload?: unknown) {
    this.listeners.get(event)?.forEach((cb) => cb(payload))
  }

  boot() {
    if (this.frameTimer !== null) return
    const scene = makeCanvas()
    this.rgbCanvasCtx = scene?.ctx ?? null

    setTimeout(() => {
      this.cameraStatus = 'connected'
      this.emit('camera.status', { status: 'connected' })
      this.startFrameLoop()
    }, 1400)
  }

  startFrameLoop() {
    if (this.frameTimer !== null || this.cameraStatus !== 'connected') return
    this.frameTimer = setInterval(() => {
      this.t += 120
      const dataUrl = this.renderFrame(this.t)
      if (!dataUrl) return
      this.lastRgbDataUrl = dataUrl.rgb
      this.emit('camera.frame', dataUrl.rgbPayload)
      this.emit('camera.frame', dataUrl.depthPayload)
    }, 120)
  }

  stopFrameLoop() {
    if (this.frameTimer !== null) {
      clearInterval(this.frameTimer)
      this.frameTimer = null
    }
  }

  private renderFrame(t: number) {
    const ctx = this.rgbCanvasCtx
    if (!ctx) return null
    drawScene(ctx, t, false)
    const rgb = ctx.canvas.toDataURL('image/jpeg', 0.62)
    drawScene(ctx, t, true)
    const depth = ctx.canvas.toDataURL('image/jpeg', 0.62)
    const [rw, rh] = this.settings.rgbResolution.split('x').map(Number)
    const [dw, dh] = this.settings.depthResolution.split('x').map(Number)
    return {
      rgb: rgb,
      rgbPayload: {
        stream: 'rgb',
        dataUrl: rgb,
        width: rw,
        height: rh,
        fps: this.settings.fps,
        timestamp: Date.now(),
      },
      depthPayload: {
        stream: 'depth',
        dataUrl: depth,
        width: dw,
        height: dh,
        fps: this.settings.fps,
        timestamp: Date.now(),
      },
    }
  }

  getDepthSample(x: number, y: number): number | null {
    const d = Math.hypot(x - RGB_W / 2, y - RGB_H * 0.55)
    if (d > 150) return null
    return Math.round((0.21 + (d / 150) * 2.4) * 100) / 100
  }

  applySettings(next: Partial<CameraSettings>): Promise<{ restartRequired: boolean }> {
    this.streamRestarting = true
    this.cameraStatus = 'reconnecting'
    this.emit('camera.status', { status: 'reconnecting' })
    this.stopFrameLoop()
    Object.assign(this.settings, next)
    return new Promise((resolve) => {
      setTimeout(() => {
        this.cameraStatus = 'connected'
        this.emit('camera.status', { status: 'connected' })
        this.streamRestarting = false
        this.startFrameLoop()
        resolve({ restartRequired: true })
      }, 900)
    })
  }

  setStoragePath(path: string) {
    this.storage.path = path
    this.storage.usedByDatasetGb = Math.round(Math.random() * 90) / 100 + 0.4
    this.emit('storage.updated', this.storageSnapshot())
  }

  browsePath(): Promise<string | null> {
    this.browseIndex = (this.browseIndex + 1) % (this.browseCandidates.length + 1)
    if (this.browseIndex === this.browseCandidates.length) return Promise.resolve(null)
    return Promise.resolve(this.browseCandidates[this.browseIndex] ?? null)
  }

  storageSnapshot() {
    return { ...this.storage }
  }

  startCapture(cmd: {
    mode: CaptureMode
    count: number | null
    intervalMs: number
    datasetId: string
    labelId: string
  }) {
    if (this.session || this.cameraStatus !== 'connected') {
      this.emit('capture.failed', {
        reason: 'camera_error',
        message: 'Capture cannot start while the camera is not connected.',
      })
      return
    }
    const total = cmd.mode === 'single' ? 1 : cmd.mode === 'burst' ? (cmd.count ?? 1) : null
    this.session = {
      mode: cmd.mode,
      remaining: total,
      intervalMs: Math.max(50, cmd.intervalMs),
      captured: 0,
      datasetId: cmd.datasetId,
      labelId: cmd.labelId,
    }
    this.emit('capture.started', { mode: cmd.mode, total })
    let current = 0
    const step = () => {
      const s = this.session
      if (!s) return
      current += 1
      s.captured = current
      if (s.remaining !== null) s.remaining -= 1
      this.emit('capture.progress', { current, total: s.remaining === null ? null : total })

      const pairFails = Math.random() < 0.04
      const labelName = this.labels.find((l) => l.id === s.labelId)?.name ?? 'unknown'
      const seq = String(127 + current).padStart(6, '0')

      if (pairFails) {
        this.emit('capture.completed', {
          id: seq,
          datasetName: this.datasets.find((d) => d.id === s.datasetId)?.name ?? '',
          labelName,
          rgbFilename: `rgb/${seq}.png`,
          depthFilename: `depth/${seq}.npy`,
          rgbOk: true,
          depthOk: false,
          pairOk: false,
          previewDataUrl: this.lastRgbDataUrl,
          timestamp: Date.now(),
        })
        this.recent.unshift({
          id: seq,
          datasetId: s.datasetId,
          labelId: s.labelId,
          labelName,
          rgbFilename: `rgb/${seq}.png`,
          depthFilename: `depth/${seq}.npy`,
          pairOk: false,
          timestamp: Date.now(),
        })
      } else {
        this.statistics[s.datasetId] ??= {}
        this.statistics[s.datasetId]![s.labelId] =
          (this.statistics[s.datasetId]![s.labelId] ?? 0) + 1
        this.emit('dataset.updated', { datasetId: s.datasetId })
        this.emit('capture.completed', {
          id: seq,
          datasetName: this.datasets.find((d) => d.id === s.datasetId)?.name ?? '',
          labelName,
          rgbFilename: `rgb/${seq}.png`,
          depthFilename: `depth/${seq}.npy`,
          rgbOk: true,
          depthOk: true,
          pairOk: true,
          previewDataUrl: this.lastRgbDataUrl,
          timestamp: Date.now(),
        })
        this.recent.unshift({
          id: seq,
          datasetId: s.datasetId,
          labelId: s.labelId,
          labelName,
          rgbFilename: `rgb/${seq}.png`,
          depthFilename: `depth/${seq}.npy`,
          pairOk: true,
          timestamp: Date.now(),
        })
      }
      this.recent = this.recent.slice(0, 60)
      if (s.remaining !== null && s.remaining <= 0) {
        this.stopCapture(false)
      }
    }
    step()
    this.captureTimer = setInterval(step, this.session.intervalMs)
  }

  stopCapture(byUser: boolean) {
    if (byUser) this.emit('capture.progress', { current: this.session?.captured ?? 0, total: null })
    if (this.captureTimer !== null) {
      clearInterval(this.captureTimer)
      this.captureTimer = null
    }
    this.session = null
  }

  isCapturing(): boolean {
    return this.session !== null
  }

  getRecentCaptures(datasetId: string, labelId: string) {
    return this.recent.filter(
      (r) => r.datasetId === datasetId && r.labelId === labelId,
    )
  }

  deleteCapture(id: string, datasetId: string, labelId: string): Promise<{ ok: boolean }> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const stat = this.statistics[datasetId]?.[labelId]
        if (stat && stat > 0) {
          this.statistics[datasetId]![labelId] = stat - 1
          this.emit('dataset.updated', { datasetId })
        }
        resolve({ ok: true })
      }, 600)
    })
  }

  retakeCapture(id: string): Promise<{ ok: boolean }> {
    return new Promise((resolve) => setTimeout(() => resolve({ ok: true }), 500))
  }
}

export const mockEngine = new MockEngine()
