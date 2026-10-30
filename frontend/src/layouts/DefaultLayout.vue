<script setup lang="ts">
import { RouterView } from 'vue-router'

import AppSidebar from '@/components/layout/AppSidebar.vue'
import BackendOfflineNotice from '@/components/common/BackendOfflineNotice.vue'
</script>

<template>
  <div class="min-h-dvh">
    <AppSidebar />
    <!-- Canvas: rail 80 + 32 padding each side; a 16px gutter and a 64px bottom bar on the phone. -->
    <main class="min-w-0 px-4 pt-5 pb-24 md:ml-[var(--rail-width)] md:px-8 md:pt-7 md:pb-10">
      <BackendOfflineNotice />
      <RouterView />
    </main>
  </div>
</template>
