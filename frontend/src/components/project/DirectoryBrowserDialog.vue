<script setup lang="ts">
import { ChevronUp, Folder, FolderPlus } from '@lucide/vue'
import { ref, watch } from 'vue'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { errorMessage } from '@/services/api'
import { systemService } from '@/services/systemService'
import type { DirectoryListing } from '@/types'

// Fallback when the operating system offers no folder dialog to the backend.
const props = defineProps<{ initial?: string }>()
const open = defineModel<boolean>('open', { required: true })
const emit = defineEmits<{ choose: [path: string] }>()

const listing = ref<DirectoryListing | null>(null)
const error = ref<string | null>(null)
const newName = ref('')
const creating = ref(false)

async function go(path?: string) {
  try {
    listing.value = await systemService.listDirectory(path)
    error.value = null
  } catch (err) {
    error.value = errorMessage(err)
  }
}

async function createFolder() {
  if (!listing.value || !newName.value.trim()) return
  try {
    const made = await systemService.createDirectory(listing.value.path, newName.value)
    newName.value = ''
    creating.value = false
    await go(made.path)
  } catch (err) {
    error.value = errorMessage(err)
  }
}

watch(open, (isOpen) => isOpen && go(props.initial || undefined), { immediate: true })

function choose() {
  if (!listing.value) return
  emit('choose', listing.value.path)
  open.value = false
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="sm:max-w-2xl">
      <DialogHeader>
        <DialogTitle>Choose destination folder</DialogTitle>
        <DialogDescription class="text-subtle">Folders on the computer running the backend.</DialogDescription>
      </DialogHeader>

      <div v-if="listing" class="grid gap-4 sm:grid-cols-[150px_minmax(0,1fr)]">
        <ul class="flex flex-wrap gap-1 sm:flex-col" aria-label="Places">
          <li v-for="s in listing.shortcuts" :key="s.path">
            <button
              type="button"
              class="w-full rounded-sm px-2 py-1.5 text-left text-subtle hover:bg-raised hover:text-ink"
              @click="go(s.path)"
            >
              {{ s.name }}
            </button>
          </li>
        </ul>

        <div class="min-w-0">
          <div class="mb-2 flex items-center gap-2">
            <Button size="icon-sm" variant="outline" :disabled="!listing.parent" aria-label="Up one folder" @click="go(listing.parent ?? undefined)">
              <ChevronUp />
            </Button>
            <p class="min-w-0 flex-1 truncate font-mono text-small text-subtle" :title="listing.path">{{ listing.path }}</p>
            <Button size="sm" variant="outline" @click="creating = !creating"><FolderPlus />New folder</Button>
          </div>

          <form v-if="creating" class="mb-2 flex gap-2" @submit.prevent="createFolder">
            <Input v-model="newName" placeholder="Folder name" aria-label="New folder name" autofocus />
            <Button type="submit" size="default" variant="outline">Create</Button>
          </form>

          <ul class="h-72 overflow-y-auto rounded-sm border border-border">
            <li v-for="entry in listing.entries" :key="entry.path">
              <button
                type="button"
                class="flex h-9 w-full items-center gap-2.5 border-b border-rule px-3 text-left hover:bg-raised"
                @click="go(entry.path)"
              >
                <Folder class="size-4 text-subtle" :stroke-width="1.5" />
                <span class="truncate">{{ entry.name }}</span>
              </button>
            </li>
            <li v-if="!listing.entries.length" class="px-3 py-3 text-subtle">No sub-folders here.</li>
          </ul>
        </div>
      </div>

      <p v-if="error" class="text-negative">{{ error }}</p>

      <DialogFooter>
        <Button variant="outline" @click="open = false">Cancel</Button>
        <Button :disabled="!listing" @click="choose">Use this folder</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
