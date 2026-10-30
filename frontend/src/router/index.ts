import { createRouter, createWebHistory } from 'vue-router'

import DefaultLayout from '@/layouts/DefaultLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: DefaultLayout,
      children: [
        { path: '', redirect: '/capture' },
        {
          path: 'capture',
          name: 'capture',
          component: () => import('@/views/CaptureView.vue'),
          meta: { title: 'Capture' },
        },
        {
          path: 'history',
          name: 'history',
          component: () => import('@/views/HistoryView.vue'),
          meta: { title: 'History' },
        },
        {
          path: 'settings',
          component: () => import('@/views/settings/SettingsView.vue'),
          children: [
            { path: '', redirect: '/settings/camera' },
            {
              path: 'camera',
              name: 'settings-camera',
              component: () => import('@/views/settings/CameraSettingsView.vue'),
              meta: { title: 'Camera settings' },
            },
            {
              path: 'capture',
              name: 'settings-capture',
              component: () => import('@/views/settings/CaptureRulesView.vue'),
              meta: { title: 'Capture rules' },
            },
            {
              path: 'shortcuts',
              name: 'settings-shortcuts',
              component: () => import('@/views/settings/ShortcutsView.vue'),
              meta: { title: 'Shortcuts' },
            },
          ],
        },
        { path: ':pathMatch(.*)*', redirect: '/capture' },
      ],
    },
  ],
})

router.afterEach((to) => {
  const title = to.meta.title as string | undefined
  document.title = title ? `${title} · RealSense Collector` : 'RealSense Collector'
})

export default router
