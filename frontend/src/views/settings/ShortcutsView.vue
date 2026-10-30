<script setup lang="ts">
import Kbd from '@/components/common/Kbd.vue'
import SettingsRow from '@/components/common/SettingsRow.vue'
import { SHORTCUTS } from '@/constants/shortcuts'
</script>

<template>
  <div class="divide-y divide-border">
    <SettingsRow
      title="Capture screen keys"
      description="These keys work only on the Capture screen, and not while you type in a field or a dialog is open."
    >
      <table class="w-full border-collapse">
        <thead>
          <tr class="h-10 text-left text-small text-subtle">
            <th scope="col" class="w-48 font-normal">Keys</th>
            <th scope="col" class="font-normal">Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in SHORTCUTS" :key="s.action" class="h-12 border-t border-rule">
            <td>
              <span class="flex items-center gap-1.5">
                <template v-for="(k, i) in s.label" :key="k">
                  <span v-if="i" class="text-small text-subtle">or</span>
                  <Kbd>{{ k }}</Kbd>
                </template>
              </span>
            </td>
            <td>{{ s.description }}</td>
          </tr>
        </tbody>
      </table>
    </SettingsRow>

    <SettingsRow title="Why these keys" description="Picked so they never clash with the browser.">
      <ul class="grid gap-2 text-subtle">
        <li><span class="text-ink">Space</span> only scrolls a page by default; on Capture it is taken over.</li>
        <li><span class="text-ink">Arrow keys</span> have no job on a page that does not scroll sideways.</li>
        <li><span class="text-ink">Alt + arrows</span> were avoided: they are the browser's back and forward.</li>
        <li><span class="text-ink">Ctrl and ⌘ combinations</span> were avoided: the browser owns most of them.</li>
      </ul>
    </SettingsRow>
  </div>
</template>
