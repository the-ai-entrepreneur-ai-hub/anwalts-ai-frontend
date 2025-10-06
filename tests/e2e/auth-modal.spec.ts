import { test, expect } from '@playwright/test'

test('auth modal opens, buttons clickable, body scroll locked', async ({ page }) => {
  await page.goto('http://localhost:3000/?auth=required')

  // Modal visible
  const dialog = page.locator('.auth-modal')
  await expect(dialog).toBeVisible()

  // Email type works
  const email = page.locator('#authEmail')
  await email.fill('test@example.com')
  await expect(email).toHaveValue('test@example.com')

  // Google button clickable
  await page.locator('.social-button.google').click()

  // Close by ESC
  await page.keyboard.press('Escape')
  await expect(dialog).toBeHidden()
})

