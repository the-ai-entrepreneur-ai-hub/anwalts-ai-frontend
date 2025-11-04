import { test, expect } from '@playwright/test'
import { Buffer } from 'node:buffer'

interface TemplateRecord {
  id: string
  title: string
  content: string
  category?: string
  type?: string
  created_at?: string
  updated_at?: string
}

test('templates catalog supports CRUD and dynamic data', async ({ page }) => {
  const templates: TemplateRecord[] = [
    {
      id: 'tpl-1',
      title: 'Arbeitsvertrag – Standard',
      content: '<p>Arbeitsvertrag Beispiel</p>',
      category: 'Arbeitsrecht',
      type: 'document',
      created_at: '2024-06-01T08:00:00',
      updated_at: '2024-06-15T10:12:00'
    },
    {
      id: 'tpl-2',
      title: 'NDA – Startups',
      content: '<p>NDAs für Startups</p>',
      category: 'Vertrag',
      type: 'document',
      created_at: '2024-06-10T09:30:00',
      updated_at: '2024-06-18T09:30:00'
    }
  ]

  const clauses = [
    { id: 'c1', title: 'Vertraulichkeit', content: 'Der Mandant verpflichtet sich zur Verschwiegenheit.', summary: 'Schützt sensible Informationen.' },
    { id: 'c2', title: 'Gerichtsstand', content: 'Erfüllungsort ist Berlin.', summary: 'Regelt zuständiges Gericht.' }
  ]

  const fulfillTemplates = async (route: any) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(templates)
    })
  }

  await page.route('**/api/templates', async (route) => {
    const method = route.request().method()
    if (method === 'GET') {
      return fulfillTemplates(route)
    }

    if (method === 'POST') {
      const payload = route.request().postDataJSON() as Record<string, any>
      const now = new Date().toISOString()
      const created: TemplateRecord = {
        id: `tpl-${Math.random().toString(36).slice(2, 8)}`,
        title: payload.title,
        content: payload.content,
        category: payload.category || null,
        type: payload.type || 'document',
        created_at: now,
        updated_at: now
      }
      templates.unshift(created)
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(created)
      })
    }

    return route.continue()
  })

  await page.route('**/api/templates/*', async (route) => {
    const method = route.request().method()
    if (method === 'PUT') {
      const payload = route.request().postDataJSON() as Record<string, any>
      const id = route.request().url().split('/').pop() || ''
      const existing = templates.find((item) => item.id === id)
      if (!existing) {
        return route.fulfill({ status: 404, contentType: 'application/json', body: JSON.stringify({ detail: 'Not found' }) })
      }
      existing.title = payload.title || existing.title
      existing.content = payload.content || existing.content
      existing.category = payload.category || existing.category
      existing.updated_at = new Date().toISOString()
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(existing)
      })
    }
    if (method === 'DELETE') {
      const url = new URL(route.request().url())
      const id = url.pathname.split('/').pop() || ''
      const index = templates.findIndex((item) => item.id === id)
      if (index !== -1) {
        templates.splice(index, 1)
      }
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ message: 'deleted' }) })
    }
    return route.continue()
  })

  await page.route('**/api/templates/insights', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        counts: { active: templates.length, updated_recent: 1, usage_events: 0 },
        last_updated_at: templates[0].updated_at,
        suggestions: templates.map((tpl, index) => ({
          id: tpl.id,
          name: tpl.title,
          category: tpl.category,
          usage_count: 5 - index,
          match_score: 80 - index * 5,
          updated_at: tpl.updated_at
        })),
        top_categories: [
          { label: 'Arbeitsrecht', count: 1 },
          { label: 'Vertrag', count: 1 }
        ],
        recent_templates: templates
      })
    })
  })

  await page.route('**/api/documents/clauses', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(clauses)
      })
      return
    }
    return route.continue()
  })

  await page.route('**/api/clauses', async (route) => {
    if (route.request().method() === 'POST') {
      const payload = route.request().postDataJSON() as Record<string, any>
      const summary = String(payload.content || '').slice(0, 120) || payload.title
      const created = {
        id: `c-${Math.random().toString(36).slice(2, 8)}`,
        title: payload.title,
        content: payload.content,
        summary,
        category: payload.category,
        language: payload.language
      }
      clauses.unshift(created)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(created)
      })
      return
    }

    if (route.request().method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(clauses)
      })
      return
    }

    return route.continue()
  })

  await page.goto('http://localhost:3000/templates')

  await expect(page.getByRole('heading', { name: 'Vorlageninventar' })).toBeVisible()
  const templateCard = (title: string) => page.locator('.template-card').filter({ hasText: title })
  await expect(templateCard('Arbeitsvertrag – Standard')).toHaveCount(1)

  await page.fill('#templateSearch', 'Startups')
  await expect(templateCard('NDA – Startups')).toHaveCount(1)
  await expect(templateCard('Arbeitsvertrag – Standard')).toHaveCount(0)

  await page.fill('#templateSearch', '')
  await expect(templateCard('Arbeitsvertrag – Standard')).toHaveCount(1)
  await page.waitForFunction(() => {
    return Array.from(document.querySelectorAll('.template-card .template-title')).some((el) =>
      el.textContent?.includes('Arbeitsvertrag – Standard')
    )
  })

  await page.locator('.templates-panel').getByRole('button', { name: 'Neue Vorlage' }).first().click()
  await page.fill('input[placeholder="Vorlagenname eingeben"]', 'Vergleich Angebot')
  await page.fill('textarea[placeholder="Vorlageninhalt eingeben"]', 'Vergleichsentwurf mit Rahmendaten.')
  const createRequest = page.waitForRequest((req) => req.url().includes('/api/templates') && req.method() === 'POST')
  await page.getByRole('button', { name: 'Vorlage erstellen' }).click()
  const postCall = await createRequest
  expect(postCall.postDataJSON()?.title).toBe('Vergleich Angebot')
  await expect(templateCard('Vergleich Angebot')).toHaveCount(1)

  await page.getByTitle('Vergleich Angebot bearbeiten').click()
  await page.fill('textarea[placeholder="Vorlageninhalt eingeben"]', 'Aktualisierter Vergleichstext')
  const updateRequest = page.waitForRequest((req) => req.url().includes('/api/templates/') && req.method() === 'PUT')
  await page.getByRole('button', { name: 'Änderungen speichern' }).click()
  await updateRequest
  await expect(page.locator('.template-card').filter({ hasText: 'Aktualisierter Vergleichstext' })).toHaveCount(1)

  page.once('dialog', (dialog) => dialog.accept())
  await page.getByTitle('Vergleich Angebot löschen').click()
  await expect(templateCard('Vergleich Angebot')).toHaveCount(0)

  await page.getByRole('button', { name: 'Neue Klausel' }).first().click()
  await page.getByLabel('Titel').fill('Sicherung Eigentum übertragen')
  await page.getByLabel('Kategorie').fill('Sicherungsrechte')
  await page.getByLabel('Inhalt').fill('Der Mandant bestätigt die Sicherungsübereignung nach deutschem Recht.')

  const clauseCreateRequest = page.waitForRequest((req) => req.url().includes('/api/clauses') && req.method() === 'POST')
  const clauseReload = page.waitForResponse((resp) => resp.url().includes('/api/documents/clauses') && resp.request().method() === 'GET')
  await page.getByRole('button', { name: 'Klausel speichern' }).click()
  await clauseCreateRequest
  await clauseReload
  await expect(page.locator('.clause-list').getByText('Sicherung Eigentum übertragen', { exact: false })).toBeVisible()
})

test('import button uploads document and adds template to catalogue', async ({ page }) => {
  const initialTemplates: TemplateRecord[] = [
    {
      id: 'tpl-existing',
      title: 'Mandantenanschreiben',
      content: '<p>Standardanschreiben</p>',
      category: 'Allgemein',
      type: 'document',
      created_at: '2024-06-01T08:00:00',
      updated_at: '2024-06-10T08:00:00'
    }
  ]

  const importedTemplate: TemplateRecord = {
    id: 'tpl-imported',
    title: 'Importierte Vorlage',
    content: '<p>[Mandant] – importierter Inhalt</p>',
    category: 'Importiert',
    type: 'document',
    created_at: '2024-10-19T20:00:00',
    updated_at: '2024-10-19T20:00:00'
  }

  await page.route('**/api/templates', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(initialTemplates)
      })
      return
    }
    route.continue()
  })

  await page.route('**/api/templates/insights', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        counts: { active: initialTemplates.length, updated_recent: 0, usage_events: 0 },
        last_updated_at: initialTemplates[0].updated_at,
        suggestions: [],
        top_categories: [],
        recent_templates: initialTemplates
      })
    })
  })

  await page.route('**/api/documents/clauses', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([])
    })
  })

  const importCall = page.waitForRequest('**/api/templates/import')

  await page.route('**/api/templates/import', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(importedTemplate)
    })
  })

  await page.goto('http://localhost:3000/templates')
  await expect(page.locator('.template-card').filter({ hasText: 'Mandantenanschreiben' })).toHaveCount(1)

  await page.click('button:has-text("Importieren")')
  await page.setInputFiles('input[type="file"]', {
    name: 'import.pdf',
    mimeType: 'application/pdf',
    buffer: Buffer.from('Beispielinhalt für die importierte Vorlage')
  })

await importCall
await expect(page.locator('.toast-title', { hasText: 'Vorlage importiert' })).toBeVisible()
await expect(page.locator('.template-card').first()).toContainText('Importierte Vorlage')
})

test('clause sidebar falls back to curated suggestions when API empty', async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: {
        writeText: (text: string) => {
          // @ts-ignore
          window.__copiedText = text
          return Promise.resolve()
        }
      }
    })
    // @ts-ignore
    window.__copiedText = ''
  })

  const templates: TemplateRecord[] = [
    {
      id: 'tpl-fall-1',
      title: 'Arbeitsvertrag – Standard',
      content: '<p>Arbeitsvertrag Beispiel</p>',
      category: 'Arbeitsrecht',
      type: 'document',
      created_at: '2024-05-01T08:00:00',
      updated_at: '2024-06-01T08:00:00'
    }
  ]

  await page.route('**/api/templates', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(templates)
      })
      return
    }
    return route.continue()
  })

  await page.route('**/api/templates/insights', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        counts: { active: templates.length, updated_recent: 1, usage_events: 0 },
        last_updated_at: templates[0].updated_at,
        suggestions: [],
        top_categories: [{ label: 'Arbeitsrecht', count: 1 }],
        recent_templates: templates
      })
    })
  })

  await page.route('**/api/documents/clauses', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      })
      return
    }
    return route.continue()
  })

  await page.goto('http://localhost:3000/templates')

  await page.waitForFunction(() => document.querySelectorAll('.clause-list .clause-pill').length > 0)
  await expect(page.locator('.clause-list .clause-pill').getByText('Treu und Glauben (§ 242 BGB)')).toBeVisible()
  const clauseCount = await page.locator('.clause-list .clause-pill').count()
  expect(clauseCount).toBeGreaterThanOrEqual(4)
  await expect(page.locator('.clause-list .clause-pill').filter({ hasText: 'Kernbaustein' })).toHaveCount(0)
  await expect(page.locator('.clause-badge', { hasText: 'Vorschlag' }).first()).toBeVisible()

  await page.locator('.clause-pill').first().click()
  const copied = await page.evaluate(() => (window as any).__copiedText)
  expect(copied).not.toBe('')
})
