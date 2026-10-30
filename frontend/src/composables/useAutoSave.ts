import { ref } from 'vue'

import { errorMessage } from '@/services/api'

export type SaveState = 'idle' | 'saving' | 'saved' | 'error'

/** Controls that save themselves: run the save, then show a quiet "Saved" stamp. */
export function useAutoSave() {
  const state = ref<SaveState>('idle')
  const error = ref<string | null>(null)
  let clear: number | null = null

  async function run<T>(save: () => Promise<T>): Promise<T | undefined> {
    if (clear) clearTimeout(clear)
    state.value = 'saving'
    try {
      const result = await save()
      state.value = 'saved'
      error.value = null
      clear = window.setTimeout(() => (state.value = 'idle'), 2000)
      return result
    } catch (err) {
      state.value = 'error'
      error.value = errorMessage(err)
      return undefined
    }
  }

  return { state, error, run }
}
