// Capture-screen shortcuts. Chosen because the browser gives them no default
// action on a page without text focus: Space would only scroll (prevented here),
// and the bare arrow keys do nothing on a page that does not scroll sideways.
// Ctrl/Alt combinations were avoided: Alt+←/→ is browser back/forward and most
// Ctrl+key pairs belong to the browser.

export type ShortcutAction = 'capture' | 'nextClass' | 'prevClass' | 'cancel'

export interface Shortcut {
  action: ShortcutAction
  keys: string[] // KeyboardEvent.code values
  label: string[] // what is printed on the key caps
  description: string
}

export const SHORTCUTS: Shortcut[] = [
  { action: 'capture', keys: ['Space'], label: ['Space'], description: 'Take a picture (starts the timer when one is set)' },
  { action: 'nextClass', keys: ['ArrowRight', 'ArrowDown'], label: ['→', '↓'], description: 'Next class' },
  { action: 'prevClass', keys: ['ArrowLeft', 'ArrowUp'], label: ['←', '↑'], description: 'Previous class' },
  { action: 'cancel', keys: ['Escape'], label: ['Esc'], description: 'Cancel a running countdown' },
]

export function shortcutFor(action: ShortcutAction): Shortcut {
  return SHORTCUTS.find((s) => s.action === action)!
}
