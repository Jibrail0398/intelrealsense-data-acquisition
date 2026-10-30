<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { toast } from 'vue-sonner'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogScrollContent,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { DEFAULT_FORMATS } from '@/constants/capture'
import { errorMessage } from '@/services/api'
import { useProjectStore } from '@/stores/projects'
import type { FormatKey } from '@/types'

import ClassListInput from './ClassListInput.vue'
import DirectoryField from './DirectoryField.vue'
import FormatChecklist from './FormatChecklist.vue'
import LayoutPreview from './LayoutPreview.vue'

const open = defineModel<boolean>('open', { required: true })
const projects = useProjectStore()

const form = reactive({
  name: '',
  classes: [] as string[],
  formats: [...DEFAULT_FORMATS] as FormatKey[],
  destination: '',
})
const saving = ref(false)
const error = ref<string | null>(null)

watch(open, (isOpen) => {
  if (!isOpen) return
  Object.assign(form, { name: '', classes: [], formats: [...DEFAULT_FORMATS], destination: '' })
  error.value = null
})

const missing = computed(() => {
  if (!form.name.trim()) return 'Name the project'
  if (!form.classes.length) return 'Add at least one class'
  if (!form.formats.length) return 'Choose at least one output format'
  if (!form.destination.trim()) return 'Choose a destination folder'
  return null
})

async function submit() {
  if (missing.value) {
    error.value = missing.value
    return
  }
  saving.value = true
  try {
    const project = await projects.create({
      name: form.name.trim(),
      classes: form.classes,
      formats: form.formats,
      destination_dir: form.destination.trim(),
    })
    toast.success(`Project ${project.name} created`, { description: project.destination_dir })
    open.value = false
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogScrollContent class="sm:max-w-3xl">
      <DialogHeader>
        <DialogTitle>New project</DialogTitle>
        <DialogDescription class="text-subtle">
          A project fixes the classes, the file formats and the folder every shot is saved to.
        </DialogDescription>
      </DialogHeader>

      <form id="create-project" class="grid gap-6 md:grid-cols-[minmax(0,1fr)_260px]" @submit.prevent="submit">
        <div class="grid content-start gap-5">
          <div class="grid gap-2">
            <Label for="project-name">Project name</Label>
            <Input id="project-name" v-model="form.name" placeholder="Posyandu Melati, Oct 2026" autofocus />
          </div>

          <div class="grid gap-2">
            <Label for="project-classes">Classes</Label>
            <ClassListInput id="project-classes" v-model="form.classes" described-by="classes-help" />
            <p id="classes-help" class="text-small text-subtle">
              Each class gets its own folder; files are named after it, e.g. stunting-0001.
            </p>
          </div>

          <div class="grid gap-2">
            <Label>Output formats</Label>
            <FormatChecklist v-model="form.formats" />
          </div>

          <div class="grid gap-2">
            <Label for="project-dest">Destination folder</Label>
            <DirectoryField id="project-dest" v-model="form.destination" />
          </div>
        </div>

        <div class="min-w-0">
          <p class="mb-2 text-subtle">What will be written</p>
          <LayoutPreview :destination="form.destination" :formats="form.formats" :classes="form.classes" />
        </div>
      </form>

      <p v-if="error" class="text-negative" role="alert">{{ error }}</p>

      <DialogFooter>
        <Button variant="outline" @click="open = false">Cancel</Button>
        <Button type="submit" form="create-project" :disabled="saving">
          {{ saving ? 'Creating…' : 'Create project' }}
        </Button>
      </DialogFooter>
    </DialogScrollContent>
  </Dialog>
</template>
