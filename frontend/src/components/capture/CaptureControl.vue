<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

import Kbd from '@/components/common/Kbd.vue'
import { Button } from '@/components/ui/button'
import { useCameraStore } from '@/stores/camera'
import { useCaptureStore } from '@/stores/capture'
import { useProjectStore } from '@/stores/projects'
import { plural, relativePath } from '@/utils/format'

const capture = useCaptureStore()
const camera = useCameraStore()
const projects = useProjectStore()

// Re-evaluated whenever the camera or the selection changes.
const blocked = computed(() => {
  void camera.status
  void projects.activeClass
  return capture.blockedReason()
})

const rule = computed(() => {
  const r = capture.rules
  const parts = [plural(r.images_per_take, 'image')]
  if (r.images_per_take > 1) parts.push(`${r.burst_interval_ms} ms apart`)
  parts.push(r.timer_seconds ? `${r.timer_seconds} s timer` : 'no timer')
  return parts.join(' · ')
})

const fileCount = computed(() => capture.rules.images_per_take * (projects.activeProject?.formats.length ?? 0))

const paths = computed(() => {
  const project = projects.activeProject
  const next = capture.nextName
  if (!project || !next) return []
  return Object.values(next.paths).map((p) => relativePath(p!, project.destination_dir))
})

const label = computed(() => {
  if (capture.busy) {
    const p = capture.progress
    return p && p.total > 1 ? `Saving ${p.done} of ${p.total}…` : 'Saving…'
  }
  return 'Capture'
})
</script>

<template>
  <section class="flex flex-col rounded-md border border-border bg-surface px-5 pt-4 pb-5 shadow-[var(--shadow)]" aria-labelledby="next-heading">
    <header class="mb-2 flex items-center justify-between">
      <h2 id="next-heading" class="text-base font-semibold">Next shot</h2>
      <span class="font-mono text-ink">{{ capture.nextName?.image_name ?? '—' }}</span>
    </header>

    <ul class="mb-3 grid gap-1 font-mono text-subtle" aria-label="Files the next shot writes">
      <li v-for="p in paths" :key="p" class="truncate" :title="p">{{ p }}</li>
      <li v-if="!paths.length" class="text-faint">—</li>
    </ul>

    <p class="mb-4 flex items-center justify-between gap-3 text-small text-subtle">
      <span>{{ rule }} · {{ plural(fileCount, 'file') }}</span>
      <RouterLink to="/settings/capture" class="shrink-0 hover:text-ink">Change</RouterLink>
    </p>

    <div class="mt-auto">
    <div v-if="capture.countdown !== null" class="grid grid-cols-[minmax(0,1fr)_auto] gap-2">
      <div class="flex h-11 items-center justify-center rounded-md bg-raised font-medium num" role="status">
        Capturing in {{ capture.countdown }} s
      </div>
      <Button variant="outline" class="h-11" @click="capture.cancel">Cancel <Kbd>Esc</Kbd></Button>
    </div>
    <Button
      v-else
      class="h-11 w-full text-[15px]"
      :disabled="!!blocked || capture.busy"
      :aria-describedby="blocked ? 'capture-blocked' : undefined"
      @click="capture.trigger"
    >
      {{ label }}
      <Kbd v-if="!capture.busy" class="border-transparent bg-[#e4e4e6] text-[#131217]">Space</Kbd>
    </Button>
    <p v-if="blocked && !capture.busy" id="capture-blocked" class="mt-2 text-small text-subtle">{{ blocked }}</p>
    </div>
  </section>
</template>
