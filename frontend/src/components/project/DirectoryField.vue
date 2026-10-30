<script setup lang="ts">
import { FolderOpen } from '@lucide/vue'
import { ref } from 'vue'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ApiError, errorMessage } from '@/services/api'
import { systemService } from '@/services/systemService'

import DirectoryBrowserDialog from './DirectoryBrowserDialog.vue'

defineProps<{ id?: string; describedBy?: string }>()
const model = defineModel<string>({ required: true })

const picking = ref(false)
const browserOpen = ref(false)
const error = ref<string | null>(null)

/** Opens the operating system's own folder dialog; falls back to the in-app browser. */
async function pick() {
  picking.value = true
  error.value = null
  try {
    const picked = await systemService.pickDirectory(model.value || undefined)
    if (picked.path) model.value = picked.path
  } catch (err) {
    if (err instanceof ApiError && err.code === 'picker_unavailable') browserOpen.value = true
    else error.value = errorMessage(err)
  } finally {
    picking.value = false
  }
}
</script>

<template>
  <div>
    <div class="flex">
      <Input
        :id="id"
        v-model="model"
        class="rounded-r-none font-mono text-small"
        placeholder="/home/you/datasets/stunting"
        :aria-describedby="describedBy"
        spellcheck="false"
      />
      <Button type="button" variant="outline" class="-ml-px rounded-l-none" :disabled="picking" @click="pick">
        <FolderOpen />{{ picking ? 'Waiting for dialog…' : 'Choose folder' }}
      </Button>
    </div>
    <p v-if="error" class="mt-1.5 text-negative">{{ error }}</p>
    <DirectoryBrowserDialog v-model:open="browserOpen" :initial="model" @choose="(p) => (model = p)" />
  </div>
</template>
