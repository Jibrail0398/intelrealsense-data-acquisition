<script setup lang="ts">
import { Minus, Plus } from '@lucide/vue'
import { computed, reactive, watch } from 'vue'

import SavedStamp from '@/components/common/SavedStamp.vue'
import SettingsRow from '@/components/common/SettingsRow.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { TIMER_CHOICES } from '@/constants/capture'
import { useAutoSave } from '@/composables/useAutoSave'
import { useCaptureStore } from '@/stores/capture'
import { useProjectStore } from '@/stores/projects'
import type { CaptureRules, TimerSeconds } from '@/types'
import { plural } from '@/utils/format'

const capture = useCaptureStore()
const projects = useProjectStore()
const save = useAutoSave()

const draft = reactive<CaptureRules>({ ...capture.rules })
watch(() => capture.rules, (r) => Object.assign(draft, r))

function commit(patch: Partial<CaptureRules>) {
  Object.assign(draft, patch)
  draft.images_per_take = clamp(Math.round(draft.images_per_take), 1, 100)
  draft.burst_interval_ms = clamp(Math.round(draft.burst_interval_ms), 0, 10_000)
  void save.run(() => capture.saveRules({ ...draft }))
}

const clamp = (n: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, Number.isFinite(n) ? n : lo))

const formats = computed(() => projects.activeProject?.formats.length ?? 0)
const summary = computed(() => {
  const n = draft.images_per_take
  const parts = [`One press of Space saves ${plural(n, 'image')}`]
  if (formats.value) parts[0] += ` × ${plural(formats.value, 'format')} = ${plural(n * formats.value, 'file')}`
  if (n > 1) {
    const span = ((n - 1) * draft.burst_interval_ms) / 1000
    parts.push(`spaced ${draft.burst_interval_ms} ms apart (about ${span.toFixed(1)} s for the whole burst)`)
  }
  parts.push(draft.timer_seconds ? `after a ${draft.timer_seconds} s countdown` : 'the moment you press it')
  return parts.join(', ') + '.'
})
</script>

<template>
  <div class="divide-y divide-border">
    <SettingsRow title="Images per take" description="How many RGB-depth pairs one press of Capture saves, as a burst.">
      <template #aside><SavedStamp :state="save.state.value" :error="save.error.value" /></template>
      <div class="flex flex-wrap items-center gap-6">
        <div class="flex items-center gap-2">
          <Button size="icon" variant="outline" aria-label="One fewer" :disabled="draft.images_per_take <= 1" @click="commit({ images_per_take: draft.images_per_take - 1 })">
            <Minus />
          </Button>
          <Input
            :model-value="draft.images_per_take"
            type="number"
            min="1"
            max="100"
            class="w-20 text-center num"
            aria-label="Images per take"
            @change="(e: Event) => commit({ images_per_take: Number((e.target as HTMLInputElement).value) })"
          />
          <Button size="icon" variant="outline" aria-label="One more" :disabled="draft.images_per_take >= 100" @click="commit({ images_per_take: draft.images_per_take + 1 })">
            <Plus />
          </Button>
        </div>
        <label class="flex items-center gap-2">
          <span class="text-subtle">Interval</span>
          <Input
            :model-value="draft.burst_interval_ms"
            type="number"
            min="0"
            max="10000"
            step="50"
            class="w-24 text-right num"
            :disabled="draft.images_per_take <= 1"
            @change="(e: Event) => commit({ burst_interval_ms: Number((e.target as HTMLInputElement).value) })"
          />
          <span class="text-subtle">ms between images</span>
        </label>
      </div>
    </SettingsRow>

    <SettingsRow title="Timer" description="A countdown before the first image, so you can step back or settle the child.">
      <div role="radiogroup" aria-label="Timer" class="flex flex-wrap gap-x-6 border-b border-border">
        <button
          v-for="t in TIMER_CHOICES"
          :key="t.value"
          type="button"
          role="radio"
          :aria-checked="draft.timer_seconds === t.value"
          class="h-10 transition-colors"
          :class="draft.timer_seconds === t.value ? 'selected-line text-ink' : 'text-subtle hover:text-ink'"
          @click="commit({ timer_seconds: t.value as TimerSeconds })"
        >
          {{ t.label }}
        </button>
      </div>
    </SettingsRow>

    <SettingsRow title="What one take does" description="The result of the two settings above, for the selected project.">
      <p class="text-[15px] leading-6">{{ summary }}</p>
      <p class="mt-2 text-small text-subtle">Esc cancels a running countdown.</p>
    </SettingsRow>
  </div>
</template>
