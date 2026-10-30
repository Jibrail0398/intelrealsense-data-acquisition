<script setup lang="ts">
import { RefreshCw } from '@lucide/vue'
import { onBeforeUnmount, onMounted } from 'vue'

import PageHeader from '@/components/common/PageHeader.vue'
import HistoryFilters from '@/components/history/HistoryFilters.vue'
import HistoryTable from '@/components/history/HistoryTable.vue'
import { Button } from '@/components/ui/button'
import { eventSocket } from '@/services/eventSocket'
import { useHistoryStore } from '@/stores/history'
import { formatCount, formatTime } from '@/utils/format'

const history = useHistoryStore()

let off: (() => void) | null = null
onMounted(() => {
  void history.load()
  // New shots appear while History is open (e.g. a second window is capturing).
  off = eventSocket.on('capture.completed', () => void history.load())
})
onBeforeUnmount(() => off?.())
</script>

<template>
  <div>
    <PageHeader title="History">
      <template #subline>
        <p>
          <span class="num">{{ formatCount(history.total) }}</span> images match
          <template v-if="history.lastLoaded"> · updated {{ formatTime(history.lastLoaded) }}</template>
        </p>
      </template>
      <template #actions>
        <Button variant="outline" :disabled="history.loading" @click="history.load()"><RefreshCw />Refresh</Button>
      </template>
    </PageHeader>

    <HistoryFilters @change="history.load()" />

    <div v-if="history.error" class="rounded-md border border-border bg-surface px-5 py-4" role="alert">
      <p>Couldn't load history: {{ history.error }}</p>
      <Button class="mt-3" size="sm" variant="outline" @click="history.load()">Retry</Button>
    </div>

    <div v-else-if="!history.items.length && !history.loading" class="rounded-md border border-dashed border-control px-5 py-6 text-subtle">
      No captures match these filters. Shots taken on the Capture screen appear here with their class, project and time.
    </div>

    <template v-else>
      <HistoryTable />
      <div v-if="history.hasMore" class="mt-4">
        <Button variant="outline" :disabled="history.loading" @click="history.loadMore()">
          {{ history.loading ? 'Loading…' : 'Load 50 more' }}
        </Button>
      </div>
    </template>
  </div>
</template>
