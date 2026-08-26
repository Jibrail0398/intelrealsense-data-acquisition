import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import router from '../router'

import App from '../App.vue'

describe('App', () => {
  it('renders the application shell', async () => {
    setActivePinia(createPinia())
    const wrapper = mount(App, {
      global: {
        plugins: [router],
        stubs: {
          Teleport: { template: '<div><slot /></div>' },
        },
      },
    })
    await router.isReady()
    expect(wrapper.text()).toContain('RealSense Collector')
  })
})
