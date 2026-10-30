<script setup lang="ts">
import { ref, watch } from 'vue'
import { toast } from 'vue-sonner'

import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { errorMessage } from '@/services/api'
import { useProjectStore } from '@/stores/projects'
import type { Project } from '@/types'
import { plural } from '@/utils/format'

const props = defineProps<{ project: Project | null }>()
const open = defineModel<boolean>('open', { required: true })
const emit = defineEmits<{ deleted: [] }>()
const projects = useProjectStore()

const deleteFiles = ref(false)
const deleting = ref(false)
const error = ref<string | null>(null)

// Every opening starts from the safe choice: files stay on disk.
watch(open, (isOpen) => {
  if (!isOpen) return
  deleteFiles.value = false
  error.value = null
})

async function confirm() {
  const project = props.project
  if (!project) return
  deleting.value = true
  try {
    const result = await projects.remove(project.id, deleteFiles.value)
    open.value = false
    emit('deleted')
    if (result.errors.length) {
      toast.warning(`Project ${project.name} deleted, but some files could not be removed`, {
        description: result.errors.slice(0, 3).join('\n'),
      })
    } else if (deleteFiles.value) {
      toast.success(`Project ${project.name} deleted`, {
        description: `${plural(result.deleted_files, 'file')} and ${plural(result.deleted_folders, 'folder')} removed from disk.`,
      })
    } else {
      toast.success(`Project ${project.name} deleted`, { description: `Image files are still in ${project.destination_dir}` })
    }
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <AlertDialog v-model:open="open">
    <AlertDialogContent v-if="project" class="grid-cols-[minmax(0,1fr)]">
      <AlertDialogHeader>
        <AlertDialogTitle>Delete project {{ project.name }}?</AlertDialogTitle>
        <AlertDialogDescription class="text-subtle">
          The project, its classes and {{ plural(project.total_captures, 'history entry', 'history entries') }} are removed from the app.
        </AlertDialogDescription>
      </AlertDialogHeader>

      <label class="flex min-w-0 cursor-pointer items-start gap-3 rounded-sm bg-ground px-3 py-3">
        <Checkbox v-model="deleteFiles" class="mt-0.5" :disabled="deleting" />
        <span class="min-w-0 flex-1">
          <span class="block">Also delete its files and folders</span>
          <span v-if="deleteFiles" class="mt-1 block text-small text-negative">
            {{ plural(project.total_captures, 'image') }} and their format and class folders are permanently removed from disk.
            This cannot be undone.
          </span>
          <span v-else class="mt-1 block text-small text-subtle">Image files stay on disk.</span>
          <span class="mt-1 block truncate font-mono text-small text-faint" :title="project.destination_dir">
            {{ project.destination_dir }}
          </span>
        </span>
      </label>

      <p v-if="error" class="text-negative" role="alert">{{ error }}</p>

      <AlertDialogFooter>
        <Button variant="outline" :disabled="deleting" @click="open = false">No</Button>
        <Button
          variant="outline"
          class="border-negative text-negative hover:bg-[var(--pill-negative-bg)] hover:text-negative"
          :disabled="deleting"
          @click="confirm"
        >
          {{ deleting ? 'Deleting…' : 'Yes' }}
        </Button>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
</template>
