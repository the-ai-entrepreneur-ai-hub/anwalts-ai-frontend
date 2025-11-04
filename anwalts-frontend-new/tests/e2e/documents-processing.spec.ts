import { test, expect } from '@playwright/test'

test('documents page shows processing overlay and activates toolbar', async ({ page }) => {
  await page.route('**/api/documents/process', async (route) => {
    const rawBody = route.request().postData() || '{}'
    const body = JSON.parse(rawBody)
    const action = (body?.action || 'generate').toLowerCase()

    if (action === 'generate') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          action,
          processingState: 'generated',
          document: {
            id: 'doc_e2e',
            title: body?.payload?.title || 'Testvertrag',
            content: '<p>Generierter Mustertext</p>',
            document_type: body?.payload?.document_type || 'vertrag',
            created_at: new Date().toISOString(),
            metadata: {
              sanitized: { instructions: 'Bereinigte Angaben' },
              redactions: { '[REDACTED_EMAIL]': 1 }
            },
            processing_state: 'generated'
          },
          download: {
            docx: '/api/documents/doc_e2e/export?format=docx',
            pdf: '/api/documents/doc_e2e/export?format=pdf'
          }
        })
      })
      return
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        action,
        processingState: 'submitted',
        document: {
          id: 'doc_e2e',
          title: body?.payload?.title || 'Testvertrag',
          content: '<p>Gespeicherter Mustertext</p>',
          document_type: body?.payload?.document_type || 'vertrag',
          created_at: new Date().toISOString(),
          metadata: {
            sanitized: { instructions: 'Bereinigte Angaben' }
          },
          processing_state: 'submitted'
        },
        status: 'submitted',
        download: {
          docx: '/api/documents/doc_e2e/export?format=docx',
          pdf: '/api/documents/doc_e2e/export?format=pdf'
        }
      })
    })
  })

  page.on('console', (msg) => {
    console.log('browser:', msg.text())
  })

  await page.goto('http://localhost:3000/documents')

  await page.fill('#docType', 'Testvertrag')
  await page.fill('#requirements', 'Bitte mit vertraulichen Angaben arbeiten.')

  const overlay = page.locator('#genOverlay')
  await Promise.all([
    page.waitForRequest('**/api/documents/process'),
    page.click('#btnGenerate')
  ])

  await expect(overlay).toBeVisible()
  await expect(overlay.locator('.generate-text')).toHaveText(/Dokument wird erstellt/i)

  await page.locator('#preview:not(.hidden)').waitFor({ timeout: 5000 })
  await expect(page.locator('#preview')).toContainText('Generierter Mustertext')
  await expect(page.locator('#preview')).toContainText('Bereinigte Angaben')

  await expect(page.locator('#feedbackStatus')).toContainText(/Dokument aktualisiert/i)
  await expect(overlay).toHaveClass(/hidden/, { timeout: 5000 })
  await page.locator('#actionBar:not(.hidden)').waitFor({ timeout: 5000 })
  await expect(page.locator('#actionBar')).toBeVisible()

  await page.click('#btnSend')
  await expect(overlay).toBeVisible()
  await expect(overlay.locator('.generate-text')).toHaveText(/Dokument wird übermittelt/i)
  await expect(overlay.locator('.generate-text')).toHaveText(/Dokument übermittelt/i, { timeout: 5000 })
  await expect(page.locator('#feedbackStatus')).toContainText(/übermittelt/i)
})
