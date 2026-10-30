import type { FormatKey, OutputFormat, TimerSeconds } from '@/types'

export const TIMER_CHOICES: { value: TimerSeconds; label: string }[] = [
  { value: 0, label: 'Off' },
  { value: 3, label: '3 s' },
  { value: 5, label: '5 s' },
  { value: 10, label: '10 s' },
  { value: 20, label: '20 s' },
]

// Mirrors backend app/services/image_writer.py; the backend's /formats is the source of truth.
export const FALLBACK_FORMATS: OutputFormat[] = [
  { key: 'jpg', label: 'RGB JPG', kind: 'rgb', folder: 'jpg', ext: 'jpg', description: '8-bit colour, compressed' },
  { key: 'png', label: 'RGB PNG', kind: 'rgb', folder: 'png', ext: 'png', description: '8-bit colour, lossless' },
  { key: 'tiff', label: 'Depth TIFF', kind: 'depth', folder: 'tiff', ext: 'tiff', description: '16-bit raw depth units' },
  { key: 'png16', label: 'Depth PNG 16-bit', kind: 'depth', folder: 'png16', ext: 'png', description: '16-bit raw depth units, lossless' },
  { key: 'npy', label: 'Depth NPY', kind: 'depth', folder: 'npy', ext: 'npy', description: 'NumPy uint16 array of raw depth units' },
]

export const DEFAULT_FORMATS: FormatKey[] = ['png', 'png16', 'npy']
