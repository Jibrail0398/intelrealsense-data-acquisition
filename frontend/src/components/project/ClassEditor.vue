<script setup lang="ts">
import { ArrowDown, ArrowUp, Pencil, Trash2 } from '@lucide/vue'
import { ref } from 'vue'
import { toast } from 'vue-sonner'

import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { errorMessage } from '@/services/api'
import { useProjectStore } from '@/stores/projects'
import type { Project, ProjectClass } from '@/types'
import { formatCount } from '@/utils/format'
import { classNameProblem } from '@/utils/validators'

const props = defineProps<{ project: Project }>()
const projects = useProjectStore()

const editingId = ref<number | null>(null)
const editName = ref('')
const newName = ref('')
const error = ref<string | null>(null)
const toDelete = ref<ProjectClass | null>(null)
const confirmOpen = ref(false)

function startEdit(cls: ProjectClass) {
  editingId.value = cls.id
  editName.value = cls.name
  error.value = null
}

async function saveEdit(cls: ProjectClass) {
  const others = props.project.classes.filter((c) => c.id !== cls.id).map((c) => c.name)
  const problem = classNameProblem(editName.value, others)
  if (problem) return void (error.value = problem)
  try {
    await projects.renameClass(props.project.id, cls.id, editName.value.trim())
    if (cls.count) toast.success(`Renamed to ${editName.value.trim()}`, { description: `${cls.count} files renamed on disk` })
    editingId.value = null
    error.value = null
  } catch (err) {
    error.value = errorMessage(err)
  }
}

async function add() {
  const problem = classNameProblem(newName.value, props.project.classes.map((c) => c.name))
  if (problem) return void (error.value = problem)
  try {
    await projects.addClass(props.project.id, newName.value.trim())
    newName.value = ''
    error.value = null
  } catch (err) {
    error.value = errorMessage(err)
  }
}

function askDelete(cls: ProjectClass) {
  toDelete.value = cls
  confirmOpen.value = true
}

async function confirmDelete() {
  if (!toDelete.value) return
  try {
    await projects.removeClass(props.project.id, toDelete.value.id)
  } catch (err) {
    toast.error(errorMessage(err))
  }
}

async function move(cls: ProjectClass, delta: 1 | -1) {
  try {
    await projects.moveClass(props.project.id, cls.id, delta)
  } catch (err) {
    toast.error(errorMessage(err))
  }
}
</script>

<template>
  <div>
    <ul aria-label="Classes">
      <li
        v-for="(cls, i) in project.classes"
        :key="cls.id"
        class="grid h-11 grid-cols-[minmax(0,1fr)_auto_auto] items-center gap-3 border-b border-rule"
      >
        <form v-if="editingId === cls.id" class="flex gap-2" @submit.prevent="saveEdit(cls)">
          <Input v-model="editName" class="h-8" :aria-label="`New name for ${cls.name}`" autofocus @keydown.esc="editingId = null" />
          <Button size="sm" type="submit">Save</Button>
          <Button size="sm" variant="ghost" type="button" @click="editingId = null">Cancel</Button>
        </form>
        <span v-else class="truncate">{{ cls.name }}</span>

        <span class="num text-right text-subtle">{{ formatCount(cls.count) }}</span>

        <span class="flex items-center">
          <Button size="icon-sm" variant="ghost" :disabled="i === 0" :aria-label="`Move ${cls.name} up`" @click="move(cls, -1)">
            <ArrowUp />
          </Button>
          <Button size="icon-sm" variant="ghost" :disabled="i === project.classes.length - 1" :aria-label="`Move ${cls.name} down`" @click="move(cls, 1)">
            <ArrowDown />
          </Button>
          <Button size="icon-sm" variant="ghost" :aria-label="`Rename ${cls.name}`" @click="startEdit(cls)"><Pencil /></Button>
          <Button
            size="icon-sm"
            variant="ghost"
            :disabled="project.classes.length <= 1"
            :aria-label="`Delete ${cls.name}`"
            :title="project.classes.length <= 1 ? 'A project needs at least one class' : undefined"
            @click="askDelete(cls)"
          >
            <Trash2 />
          </Button>
        </span>
      </li>
    </ul>

    <form class="mt-3 flex gap-2" @submit.prevent="add">
      <Input v-model="newName" placeholder="New class name" aria-label="New class name" />
      <Button type="submit" variant="outline" :disabled="!newName.trim()">Add class</Button>
    </form>
    <p v-if="error" class="mt-2 text-negative" role="alert">{{ error }}</p>

    <ConfirmDialog
      v-model:open="confirmOpen"
      :title="`Delete class ${toDelete?.name}?`"
      :description="toDelete?.count
        ? `Its ${toDelete.count} images stay on disk and in History, but no new shots can be taken for it.`
        : 'It has no images yet.'"
      confirm-label="Delete class"
      destructive
      @confirm="confirmDelete"
    />
  </div>
</template>
