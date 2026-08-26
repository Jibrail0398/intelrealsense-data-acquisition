import { onMounted, onUnmounted } from 'vue'

export interface ShortcutHandlers {
  capture: () => void
  retake: () => void
  deleteLast: () => void
  stop: () => void
  toggleContinuous: () => void
}

function isTypingTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false
  const tag = target.tagName.toLowerCase()
  return (
    tag === 'input' ||
    tag === 'select' ||
    tag === 'textarea' ||
    target.isContentEditable
  )
}

export function useDashboardShortcuts(handlers: ShortcutHandlers) {
  function onKeyDown(evt: KeyboardEvent) {
    if (isTypingTarget(evt.target)) return

    switch (evt.key) {
      case ' ':
      case 'Spacebar':
        evt.preventDefault()
        handlers.capture()
        break
      case 'r':
      case 'R':
        evt.preventDefault()
        handlers.retake()
        break
      case 'Delete':
        evt.preventDefault()
        handlers.deleteLast()
        break
      case 'Escape':
        handlers.stop()
        break
      case 's':
      case 'S':
        evt.preventDefault()
        handlers.toggleContinuous()
        break
    }
  }

  onMounted(() => window.addEventListener('keydown', onKeyDown))
  onUnmounted(() => window.removeEventListener('keydown', onKeyDown))
}
