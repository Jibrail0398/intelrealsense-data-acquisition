<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { useCameraStore } from '@/stores/camera'
import { useProjectStore } from '@/stores/projects'

const camera = useCameraStore()
const projects = useProjectStore()

async function retry() {
  await camera.refreshStatus()
  if (camera.backendOnline) await projects.load()
}
</script>

<template>
  <div
    v-if="!camera.backendOnline"
    role="status"
    class="mb-5 flex flex-wrap items-center justify-between gap-3 rounded-md border border-[#3a2f17] bg-[var(--pill-warning-bg)] px-4 py-3 text-[var(--pill-warning-ink)]"
  >
    <p>
      Cannot reach the backend at <span class="font-mono">127.0.0.1:8000</span>. Start it with
      <span class="font-mono">./start.sh</span> or <span class="font-mono">uvicorn app.main:app</span> in
      <span class="font-mono">backend/</span>.
    </p>
    <Button size="sm" variant="outline" @click="retry">Retry</Button>
  </div>
</template>
