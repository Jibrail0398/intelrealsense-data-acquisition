<script setup lang="ts">
import { computed } from 'vue'
import { PhFolderOpen, PhMagnifyingGlass, PhSpinnerGap, PhLockSimple } from '@phosphor-icons/vue'

import { useStorageStore } from '@/stores/storageStore'
import { useCaptureStore } from '@/stores/captureStore'

const storage = useStorageStore()
const capture = useCaptureStore()

const locked = computed(() => capture.isCapturing || storage.settingPath)
</script>

<template>
  <section class="flex flex-col gap-2">
    <label class="text-xs font-medium uppercase tracking-wide text-zinc-500">Storage Path</label>
    <div class="flex gap-1.5">
      <div class="relative min-w-0 flex-1">
        <FolderOpen class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" weight="duotone" />
        <input
          v-if="storage.info"
          type="text"
          :value="storage.info.path"
          :readonly="locked"
          spellcheck="false"
          class="w-full truncate rounded-md border border-zinc-300 bg-white py-2 pl-9 pr-3 font-mono text-xs text-zinc-800 transition-all duration-300 hover:border-zinc-400 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600/15 disabled:bg-zinc-100 disabled:text-zinc-400"
          @change="storage.setManualPath(($event.target as HTMLInputElement).value)"
        />
        <div v-else class="skeleton h-[38px] w-full !rounded-md" />
      </div>
      <button
        :disabled="locked"
        class="flex shrink-0 items-center gap-1.5 rounded-md border border-zinc-300 px-3 py-2 text-sm font-medium text-zinc-700 transition-all duration-300 hover:border-blue-400 hover:text-blue-700 active:translate-y-[1px] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
        @click="storage.browseAndSet()"
      >
        <SpinnerGap v-if="storage.settingPath" class="h-4 w-4 animate-spin" />
        <MagnifyingGlass v-else-if="!locked && capture.isCapturing === false" class="h-4 w-4" />
        <LockSimple v-else class="h-4 w-4" />
        Browse
      </button>
    </div>
    <p v-if="capture.isCapturing" class="text-xs text-amber-700">
      Path is locked while a capture is running.
    </p>
    <p v-else class="text-xs text-zinc-400">Edit the path and press Enter, or browse.</p>
  </section>
</template>
