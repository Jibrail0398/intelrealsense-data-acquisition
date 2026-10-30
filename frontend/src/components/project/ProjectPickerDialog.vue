<script setup lang="ts">
import { Check, Trash2 } from '@lucide/vue'
import { ref } from 'vue'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { useProjectStore } from '@/stores/projects'
import type { Project } from '@/types'
import { formatCount, formatRecent, plural } from '@/utils/format'

import ProjectDeleteDialog from './ProjectDeleteDialog.vue'

const open = defineModel<boolean>('open', { required: true })
const emit = defineEmits<{ create: [] }>()
const projects = useProjectStore()

const toDelete = ref<Project | null>(null)
const deleteOpen = ref(false)

function askDelete(project: Project) {
  toDelete.value = project
  deleteOpen.value = true
}

async function choose(id: number) {
  await projects.selectProject(id)
  open.value = false
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="sm:max-w-2xl">
      <DialogHeader>
        <DialogTitle>Select project</DialogTitle>
        <DialogDescription class="text-subtle">
          Shots go to the selected project's folder, under the class chosen on the Capture screen.
        </DialogDescription>
      </DialogHeader>

      <ul v-if="projects.projects.length" class="max-h-[60vh] overflow-y-auto" aria-label="Projects">
        <li v-for="p in projects.projects" :key="p.id" class="flex items-center gap-1 border-b border-rule">
          <button
            type="button"
            class="grid min-w-0 flex-1 grid-cols-[minmax(0,1fr)_auto] items-center gap-4 rounded-sm px-3 py-3 text-left hover:bg-raised"
            :aria-current="p.id === projects.activeProjectId ? 'true' : undefined"
            @click="choose(p.id)"
          >
            <span class="min-w-0">
              <span class="flex items-center gap-2 font-medium">
                {{ p.name }}
                <Check v-if="p.id === projects.activeProjectId" class="size-4 text-signal" aria-label="Selected" />
              </span>
              <span class="mt-0.5 block truncate font-mono text-small text-subtle">{{ p.destination_dir }}</span>
              <span class="mt-0.5 block text-small text-faint">
                {{ p.classes.map((c) => c.name).join(' · ') }} · {{ p.formats.join(', ') }}
              </span>
            </span>
            <span class="text-right">
              <span class="block num">{{ formatCount(p.total_captures) }} <span class="text-subtle">images</span></span>
              <span class="block text-small text-faint">{{ formatRecent(p.updated_at) }}</span>
            </span>
          </button>
          <Button
            size="icon-sm"
            variant="ghost"
            class="text-subtle hover:text-negative"
            :aria-label="`Delete project ${p.name}`"
            title="Delete project"
            @click="askDelete(p)"
          >
            <Trash2 />
          </Button>
        </li>
      </ul>
      <div v-else class="rounded-sm border border-dashed border-control px-4 py-6 text-subtle">
        No projects yet. Create one to start capturing.
      </div>

      <DialogFooter class="items-center sm:justify-between">
        <p class="text-small text-faint">{{ plural(projects.projects.length, 'project') }}</p>
        <Button variant="outline" @click="emit('create')">New project</Button>
      </DialogFooter>

      <!-- Nested inside the picker so reka-ui stacks it above, with its own focus trap. -->
      <ProjectDeleteDialog v-model:open="deleteOpen" :project="toDelete" />
    </DialogContent>
  </Dialog>
</template>
