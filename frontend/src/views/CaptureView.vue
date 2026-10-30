<script setup lang="ts">
import { FolderOpen, Plus, Settings2 } from '@lucide/vue'
import { ref } from 'vue'

import CameraPreview from '@/components/capture/CameraPreview.vue'
import CaptureControl from '@/components/capture/CaptureControl.vue'
import ClassPanel from '@/components/capture/ClassPanel.vue'
import RecentStrip from '@/components/capture/RecentStrip.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import ProjectCreateDialog from '@/components/project/ProjectCreateDialog.vue'
import ProjectPickerDialog from '@/components/project/ProjectPickerDialog.vue'
import ProjectSettingsDialog from '@/components/project/ProjectSettingsDialog.vue'
import { Button } from '@/components/ui/button'
import { useCaptureShortcuts } from '@/composables/useCaptureShortcuts'
import { useCaptureStore } from '@/stores/capture'
import { useProjectStore } from '@/stores/projects'
import { formatCount } from '@/utils/format'

const projects = useProjectStore()
const capture = useCaptureStore()

const createOpen = ref(false)
const pickerOpen = ref(false)
const settingsOpen = ref(false)

useCaptureShortcuts({
  capture: () => capture.trigger(),
  nextClass: () => projects.stepClass(1),
  prevClass: () => projects.stepClass(-1),
  cancel: () => capture.cancel(),
})

function openCreate() {
  pickerOpen.value = false
  createOpen.value = true
}
</script>

<template>
  <div>
    <PageHeader :title="projects.activeProject?.name ?? 'Capture'">
      <template #subline>
        <p v-if="projects.activeProject" class="flex min-w-0 flex-wrap gap-x-3">
          <span class="max-w-full truncate font-mono" :title="projects.activeProject.destination_dir">
            {{ projects.activeProject.destination_dir }}
          </span>
          <span class="text-small">
            {{ projects.activeProject.formats.join(', ') }} ·
            <span class="num">{{ formatCount(projects.activeProject.total_captures) }}</span> images
          </span>
        </p>
        <p v-else>No project selected. Shots need a project for their classes, formats and folder.</p>
      </template>
      <template #actions>
        <Button variant="outline" @click="pickerOpen = true"><FolderOpen />Select project</Button>
        <Button v-if="projects.activeProject" variant="outline" @click="settingsOpen = true">
          <Settings2 />Project settings
        </Button>
        <Button variant="outline" @click="createOpen = true"><Plus />New project</Button>
      </template>
    </PageHeader>

    <!-- Grid: 1fr + 360px rail, 24px gap; the right rail holds the job, the left the evidence. -->
    <div class="grid grid-cols-[minmax(0,1fr)] gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
      <CameraPreview class="min-w-0" />

      <div class="flex flex-col gap-6">
        <template v-if="projects.activeProject">
          <ClassPanel @edit="settingsOpen = true" />
          <CaptureControl class="flex-1" />
        </template>
        <section
          v-else
          class="rounded-md border border-border bg-surface px-5 pt-4 pb-5 shadow-[var(--shadow)]"
          aria-labelledby="start-heading"
        >
          <h2 id="start-heading" class="text-base font-semibold">Start a project</h2>
          <p class="mt-2 text-subtle">
            Name the classes you will photograph, pick the RGB and depth formats, and choose the folder.
            Capturing unlocks once a project is selected.
          </p>
          <div class="mt-5 grid gap-2">
            <Button class="h-11" @click="createOpen = true">Create project</Button>
            <Button v-if="projects.projects.length" variant="outline" class="h-11" @click="pickerOpen = true">
              Select an existing project
            </Button>
          </div>
        </section>
      </div>

      <RecentStrip v-if="projects.activeProject" class="xl:col-span-2" />
    </div>

    <ProjectCreateDialog v-model:open="createOpen" />
    <ProjectPickerDialog v-model:open="pickerOpen" @create="openCreate" />
    <ProjectSettingsDialog v-model:open="settingsOpen" />
  </div>
</template>
