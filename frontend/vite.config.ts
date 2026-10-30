import { fileURLToPath, URL } from 'node:url'

import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig, loadEnv } from 'vite'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backend = env.VITE_BACKEND_URL || 'http://127.0.0.1:8000'

  return {
    plugins: [vue(), vueDevTools(), tailwindcss()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      host: '127.0.0.1',
      port: 5173,
      // The browser talks to one origin; Vite forwards REST, MJPEG and WebSocket to FastAPI.
      proxy: {
        '/api': { target: backend, changeOrigin: true, ws: true },
      },
    },
    preview: {
      port: 4173,
      proxy: {
        '/api': { target: backend, changeOrigin: true, ws: true },
      },
    },
  }
})
