import { test, expect } from '@playwright/test'

const mockTemplates = [
  {
    id: 'tpl-nav-1',
    title: 'Arbeitsvertrag Navigation',
    content: '<p>Arbeitsvertrag Navigation</p>',
    category: 'Arbeitsrecht',
    type: 'document',
    created_at: '2024-01-01T10:00:00.000Z',
    updated_at: '2024-01-02T10:00:00.000Z'
  },
  {
    id: 'tpl-nav-2',
    title: 'NDA Navigation',
    content: '<p>NDA Navigation</p>',
    category: 'Vertrag',
    type: 'document',
    created_at: '2024-01-03T10:00:00.000Z',
    updated_at: '2024-01-04T10:00:00.000Z'
  }
]

test('documents template controls navigate to templates catalog', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('anwalts_auth_token', 'test-token')
    localStorage.setItem('user_id', 'user-123')
  })

  page.on('console', (msg) => {
    console.log('browser:', msg.text())
  })

  await page.route('**/api/documents/templates', async (route) => {
    if (route.request().method() === 'GET') {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockTemplates)
      })
    }
    return route.continue()
  })

  await page.route('**/api/documents/clauses', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { id: 'clause-1', title: 'Gerichtsstand', summary: 'Zuständiges Gericht.' }
      ])
    })
  })

  await page.route('**/api/templates', async (route) => {
    if (route.request().method() === 'GET') {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockTemplates)
      })
    }
    return route.continue()
  })

  await page.route('**/api/templates/insights', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        counts: { active: mockTemplates.length, updated_recent: 1, usage_events: 0 },
        last_updated_at: mockTemplates[0].updated_at,
        suggestions: mockTemplates.map((tpl, index) => ({
          id: tpl.id,
          name: tpl.title,
          category: tpl.category,
          usage_count: 10 - index,
          match_score: 90 - index * 10,
          updated_at: tpl.updated_at
        }))
      })
    })
  })

  await page.goto('http://localhost:3000/documents')
  await expect(page.locator('#inlineTemplates')).toBeVisible()

  await page.waitForSelector('#btnTemplates', { state: 'visible' })
  await page.click('#btnTemplates')
  await page.waitForURL('**/templates?origin=documents')
  await expect(page).toHaveURL(/\/templates\?origin=documents/)
  await expect(page.getByRole('heading', { name: /Vorlagen/ })).toBeVisible()

  await page.goto('http://localhost:3000/documents')
  await expect(page.locator('#inlineTemplates')).toBeVisible()

  await page.waitForSelector('#btnTemplatesInline', { state: 'visible' })
  await page.click('#btnTemplatesInline')
  await page.waitForURL('**/templates?origin=documents')
  await expect(page).toHaveURL(/\/templates\?origin=documents/)
  await expect(page.getByRole('heading', { name: /Vorlagen/ })).toBeVisible()
})
