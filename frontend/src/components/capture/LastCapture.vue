<script setup lang="ts">
import { ref, computed } from 'vue'
import { PhCheck, PhX, PhArrowClockwise, PhTrash, PhImageSquare } from '@phosphor-icons/vue'

import { useCaptureStore } from '@/stores/captureStore'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'

const capture = useCaptureStore()
const confirmOpen = ref(false)

const timeLabel = computed(() => {
  const ts = capture.lastCapture?.timestamp
  if (!ts) return null
  return new Date(ts).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
})

function statusIcon(ok: boolean) {
  return ok ? PhCheck : PhX
}
</script>

<template>
  <section class="rounded-md border border-zinc-200 bg-white p-4">
    <header class="mb-3 flex items-center justify-between">
      <h3 class="text-xs font-semibold uppercase tracking-wide text-zinc-500">Last Capture</h3>
      <span v-if="timeLabel" class="font-mono text-[11px] text-zinc-400">{{ timeLabel }}</span>
    </header>

    <!-- Empty state -->
    <div
      v-if="!capture.lastCapture"
      class="flex flex-col items-center justify-center gap-2 rounded-md border border-dashed border-zinc-200 px-4 py-8 text-center"
    >
      <ImageSquare class="h-6 w-6 text-zinc-300" weight="duotone" />
      <p class="text-sm text-zinc-400">No capture yet.</p>
      <p class="max-w-[26ch] text-xs leading-relaxed text-zinc-400">
        Pick a label and press Space or CAPTURE to start collecting frames.
      </p>
    </div>

    <!-- Loaded -->
    <template v-else>
      <div class="flex gap-3.5">
        <div class="h-20 w-20 shrink-0 overflow-hidden rounded-md border border-zinc-200 bg-zinc-100">
          <img
            v-if="capture.lastCapture.previewDataUrl"
            :src="capture.lastCapture.previewDataUrl"
            :alt="`Preview of capture ${capture.lastCapture.id}`"
            class="h-full w-full object-cover"
          />
          <div v-else class="skeleton h-full w-full !rounded-none" />
        </div>

        <dl class="min-w-0 flex-1 font-mono text-xs leading-relaxed">
          <div class="flex justify-between gap-3">
            <dt class="shrink-0 text-zinc-400">ID</dt>
            <dd class="truncate font-semibold text-zinc-900">{{ capture.lastCapture.id }}</dd>
          </div>
          <div class="mt-1 truncate text-right text-zinc-500">
            {{ capture.lastCapture.rgbFilename }}
          </div>
          <div class="truncate text-right text-zinc-500">
            {{ capture.lastCapture.depthFilename }}
          </div>
        </dl>
      </div>

      <ul class="mt-3 grid grid-cols-3 divide-x divide-zinc-100 rounded-md bg-zinc-50 py-2 text-center">
        <li class="flex items-center justify-center gap-1.5 text-xs font-medium">
          <span class="text-zinc-400">RGB</span>
          <component
            :is="statusIcon(capture.lastCapture.rgbOk)"
            class="h-3.5 w-3.5"
            :class="capture.lastCapture.rgbOk ? 'text-emerald-600' : 'text-danger'"
            weight="bold"
          />
        </li>
        <li class="flex items-center justify-center gap-1.5 text-xs font-medium">
          <span class="text-zinc-400">Depth</span>
          <component
            :is="statusIcon(capture.lastCapture.depthOk)"
            class="h-3.5 w-3.5"
            :class="capture.lastCapture.depthOk ? 'text-emerald-600' : 'text-danger'"
            weight="bold"
          />
        </li>
        <li class="flex items-center justify-center gap-1.5 text-xs font-medium">
          <span class="text-zinc-400">Pair</span>
          <component
            :is="statusIcon(capture.lastCapture.pairOk)"
            class="h-3.5 w-3.5"
            :class="capture.lastCapture.pairOk ? 'text-emerald-600' : 'text-danger'"
            weight="bold"
          />
        </li>
      </ul>

      <p
        v-if="!capture.lastCapture.pairOk"
        class="mt-2 rounded-md border border-amber-200 bg-amber-50 px-2.5 py-1.5 text-xs leading-snug text-amber-800"
      >
        Pair incomplete — this capture will not count as a valid dataset sample.
      </p>

      <div class="mt-3 grid grid-cols-2 gap-2">
        <button
          :disabled="capture.isCapturing || capture.retaking"
          class="flex items-center justify-center gap-1.5 rounded-md border border-zinc-300 px-3 py-2 text-sm font-medium text-zinc-700 transition-all duration-300 hover:border-zinc-400 hover:bg-zinc-50 active:translate-y-[1px] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
          @click="capture.retake()"
        >
          <ArrowClockwise class="h-4 w-4" :class="{ 'animate-spin': capture.retaking }" />
          {{ capture.retaking ? 'Retaking…' : 'RETAKE' }}
        </button>
        <button
          :disabled="capture.isCapturing || capture.deleting"
          class="flex items-center justify-center gap-1.5 rounded-md bg-danger px-3 py-2 text-sm font-medium text-white transition-all duration-300 hover:bg-danger-hover active:translate-y-[1px] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
          @click="confirmOpen = true"
        >
          <Trash class="h-4 w-4" weight="fill" />
          {{ capture.deleting ? 'Deleting…' : 'DELETE' }}
        </button>
      </div>
    </template>

    <ConfirmDialog
      :open="confirmOpen"
      title="Delete capture?"
      :message="
        capture.lastCapture
          ? `Delete capture ${capture.lastCapture.id} along with its RGB and Depth files? This cannot be undone.`
          : ''
      "
      :busy="capture.deleting"
      @cancel="confirmOpen = false"
      @confirm="confirmOpen = false; capture.removeLast()"
    />
  </section>
</template>
