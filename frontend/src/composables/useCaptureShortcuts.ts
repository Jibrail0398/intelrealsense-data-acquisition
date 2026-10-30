import { onBeforeUnmount, onMounted } from 'vue'

import { SHORTCUTS, type ShortcutAction } from '@/constants/shortcuts'

/**
 * Keyboard shortcuts for the Capture screen. Call it from that view only:
 * the listener lives exactly as long as the view is mounted, so the keys do
 * nothing on History or Settings.
 */
export function useCaptureShortcuts(handlers: Record<ShortcutAction, () => void>) {
  function onKeydown(event: KeyboardEvent) {
    if (event.ctrlKey || event.metaKey || event.altKey || event.repeat) return
    if (isTyping(event.target) || document.querySelector('[role="dialog"], [role="alertdialog"], [role="listbox"], [role="menu"]')) {
      return
    }
    const shortcut = SHORTCUTS.find((s) => s.keys.includes(event.code))
    if (!shortcut) return
    event.preventDefault()
    handlers[shortcut.action]()
  }

  onMounted(() => window.addEventListener('keydown', onKeydown))
  onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
}

function isTyping(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false
  if (target.isContentEditable) return true
  const tag = target.tagName
  // A focused button would also fire on Space; the shortcut takes over instead of a double shot.
  return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT'
}
