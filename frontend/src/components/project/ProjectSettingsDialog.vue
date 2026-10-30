<script setup lang="ts">
import { Trash2 } from '@lucide/vue'
import { computed, ref, watch } from 'vue'
import { toast } from 'vue-sonner'

import SavedStamp from '@/components/common/SavedStamp.vue'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogDescription,
  DialogHeader,
  DialogScrollContent,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAutoSave } from '@/composables/useAutoSave'
import { errorMessage } from '@/services/api'
import { useProjectStore } from '@/stores/projects'
import type { FormatKey } from '@/types'

import ClassEditor from './ClassEditor.vue'
import DirectoryField from './DirectoryField.vue'
import FormatChecklist from './FormatChecklist.vue'
import ProjectDeleteDialog from './ProjectDeleteDialog.vue'

const open = defineModel<boolean>('open', { required: true })
const projects = useProjectStore()
const project = computed(() => projects.activeProject)

const name = ref('')
const destination = ref('')
const formats = ref<FormatKey[]>([])
const formatSave = useAutoSave()
const confirmOpen = ref(false)
const fieldError = ref<string | null>(null)

watch([open, project], () => {
  if (!open.value || !project.value) return
  name.value = project.value.name
  destination.value = project.value.destination_dir
  formats.value = [...project.value.formats]
}, { immediate: true })

async function saveFormats(next: FormatKey[]) {
  if (!project.value) return
  formats.value = next
  if (!next.length) {
    formatSave.state.value = 'error'
    formatSave.error.value = 'Keep at least one format'
    return
  }
  await formatSave.run(() => projects.update(project.value!.id, { formats: next }))
}

async function saveField(field: 'name' | 'destination_dir', value: string) {
  if (!project.value) return
  try {
    await projects.update(project.value.id, { [field]: value.trim() })
    fieldError.value = null
    toast.success(field === 'name' ? 'Project renamed' : 'Destination changed', {
      description: field === 'destination_dir' ? 'New shots go to the new folder; earlier files stay where they are.' : undefined,
    })
  } catch (err) {
    fieldError.value = errorMessage(err)
  }
}

</script>

<template>
  <Dialog v-model:open="open">
    <DialogScrollContent v-if="project" class="sm:max-w-2xl">
      <DialogHeader>
        <DialogTitle>Project settings</DialogTitle>
        <DialogDescription class="text-subtle">{{ project.name }} · changes apply to the next shot.</DialogDescription>
      </DialogHeader>

      <section class="grid gap-2">
        <Label for="settings-name">Name</Label>
        <form class="flex gap-2" @submit.prevent="saveField('name', name)">
          <Input id="settings-name" v-model="name" />
          <Button type="submit" variant="outline" :disabled="!name.trim() || name.trim() === project.name">Rename</Button>
        </form>
      </section>

      <section class="grid gap-2">
        <Label for="settings-dest">Destination folder</Label>
        <DirectoryField id="settings-dest" v-model="destination" />
        <div class="flex justify-end">
          <Button
            variant="outline"
            size="sm"
            :disabled="!destination.trim() || destination === project.destination_dir"
            @click="saveField('destination_dir', destination)"
          >
            Use this folder
          </Button>
        </div>
      </section>
      <p v-if="fieldError" class="text-negative" role="alert">{{ fieldError }}</p>

      <section class="grid gap-2">
        <div class="flex items-center justify-between">
          <Label>Output formats</Label>
          <SavedStamp :state="formatSave.state.value" :error="formatSave.error.value" />
        </div>
        <FormatChecklist :model-value="formats" @update:model-value="saveFormats" />
      </section>

      <section class="grid gap-2">
        <Label>Classes</Label>
        <ClassEditor :project="project" />
      </section>

      <section class="mt-2 flex flex-wrap items-center justify-between gap-3 rounded-sm bg-ground px-4 py-3">
        <p class="text-subtle">Deleting removes the project and its history. You choose whether its files go too.</p>
        <Button variant="outline" class="border-negative text-negative hover:bg-[var(--pill-negative-bg)] hover:text-negative" @click="confirmOpen = true">
          <Trash2 />Delete project
        </Button>
      </section>

      <ProjectDeleteDialog v-model:open="confirmOpen" :project="project" @deleted="open = false" />
    </DialogScrollContent>
  </Dialog>
</template>
