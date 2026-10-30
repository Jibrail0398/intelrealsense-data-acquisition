<script setup lang="ts">
import { Copy, MoreHorizontal, Trash2 } from '@lucide/vue'
import { ref } from 'vue'
import { toast } from 'vue-sonner'

import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { thumbnailUrl } from '@/constants/api'
import { errorMessage } from '@/services/api'
import { useHistoryStore } from '@/stores/history'
import type { CaptureRecord } from '@/types'
import { formatCount, formatDate, formatTime } from '@/utils/format'

const history = useHistoryStore()
const toDelete = ref<CaptureRecord | null>(null)
const confirmOpen = ref(false)

function folderOf(record: CaptureRecord): string {
  const first = Object.values(record.files)[0] ?? ''
  return first.replace(/[\\/][^\\/]+[\\/][^\\/]+[\\/][^\\/]+$/, '')
}

async function copyPath(record: CaptureRecord) {
  const paths = Object.values(record.files).join('\n')
  try {
    await navigator.clipboard.writeText(paths)
    toast.success('File paths copied')
  } catch {
    toast.error('Clipboard is not available in this browser')
  }
}

function askDelete(record: CaptureRecord) {
  toDelete.value = record
  confirmOpen.value = true
}

async function confirmDelete() {
  if (!toDelete.value) return
  const name = toDelete.value.image_name
  try {
    await history.remove(toDelete.value.id)
    toast.success(`Deleted ${name}`)
  } catch (err) {
    toast.error(errorMessage(err))
  }
}
</script>

<template>
  <div>
    <!-- Desktop and tablet: a table. Phone: two-line rows. -->
    <table class="hidden w-full table-fixed border-collapse md:table">
      <colgroup>
        <col class="w-[84px]" />
        <col />
        <col class="w-[16%]" />
        <col class="w-[18%]" />
        <col class="w-[18%]" />
        <col class="w-[130px]" />
        <col class="w-12" />
      </colgroup>
      <thead>
        <tr class="h-10 text-left text-small font-normal text-subtle">
          <th scope="col" class="font-normal"><span class="sr-only">Preview</span></th>
          <th scope="col" class="font-normal">Image name</th>
          <th scope="col" class="font-normal">Class</th>
          <th scope="col" class="font-normal">Project</th>
          <th scope="col" class="font-normal">Formats</th>
          <th scope="col" class="text-right font-normal">Captured</th>
          <th scope="col"><span class="sr-only">Actions</span></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in history.items" :key="row.id" class="h-[76px] border-t border-rule">
          <td>
            <img :src="thumbnailUrl(row.id)" alt="" class="h-12 w-16 rounded-sm bg-ground object-cover" loading="lazy" />
          </td>
          <td class="pr-4">
            <p class="truncate font-mono" :title="row.image_name">{{ row.image_name }}</p>
            <p class="truncate font-mono text-small text-faint" :title="folderOf(row)">{{ row.width }}×{{ row.height }}</p>
          </td>
          <td class="truncate pr-4">{{ row.class_name }}</td>
          <td class="truncate pr-4 text-subtle">{{ row.project_name }}</td>
          <td class="pr-4">
            <span class="flex flex-wrap gap-1">
              <span
                v-for="f in Object.keys(row.files)"
                :key="f"
                class="flex-none rounded-sm bg-raised px-1.5 py-0.5 text-small whitespace-nowrap text-[var(--pill-neutral-ink)]"
              >{{ f }}</span>
            </span>
          </td>
          <td class="text-right num">
            <p>{{ formatDate(row.captured_at) }}</p>
            <p class="text-small text-subtle">{{ formatTime(row.captured_at) }}</p>
          </td>
          <td class="text-right">
            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <Button size="icon-sm" variant="ghost" :aria-label="`Actions for ${row.image_name}`"><MoreHorizontal /></Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem @select="copyPath(row)"><Copy />Copy file paths</DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem class="text-negative" @select="askDelete(row)"><Trash2 />Delete files</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </td>
        </tr>
      </tbody>
    </table>

    <ul class="md:hidden">
      <li v-for="row in history.items" :key="row.id" class="grid grid-cols-[56px_minmax(0,1fr)_auto] items-center gap-3 border-t border-rule py-3">
        <img :src="thumbnailUrl(row.id)" alt="" class="h-[42px] w-14 rounded-sm bg-ground object-cover" loading="lazy" />
        <div class="min-w-0">
          <p class="truncate font-mono">{{ row.image_name }}</p>
          <p class="truncate text-small text-subtle">{{ row.class_name }} · {{ row.project_name }} · {{ Object.keys(row.files).join(', ') }}</p>
        </div>
        <div class="text-right text-small num">
          <p>{{ formatDate(row.captured_at) }}</p>
          <p class="text-subtle">{{ formatTime(row.captured_at) }}</p>
        </div>
      </li>
    </ul>

    <p class="mt-4 text-small text-subtle num">
      Showing {{ formatCount(history.items.length) }} of {{ formatCount(history.total) }}
    </p>

    <ConfirmDialog
      v-model:open="confirmOpen"
      :title="`Delete ${toDelete?.image_name}?`"
      :description="`Removes its ${Object.keys(toDelete?.files ?? {}).length} files from disk and its entry from History. This cannot be undone.`"
      confirm-label="Delete files"
      destructive
      @confirm="confirmDelete"
    />
  </div>
</template>
