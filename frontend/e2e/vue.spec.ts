import { expect, test } from '@playwright/test'

// Needs the backend running (CAMERA_BACKEND=mock is enough).
test('opens on the capture screen with the sidebar', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveURL(/\/capture$/)
  await expect(page.getByRole('navigation', { name: 'Main' })).toContainText('History')
  await expect(page.locator('h1')).toBeVisible()
})
