import { test, expect } from '@playwright/test'

const connectedStatusPayload = {
  connected: true,
  oauth_consent: true,
  ai_read_consent: true,
  draft_only_mode: false,
  consent_timestamp: new Date().toISOString(),
  active_account: {
    id: 'test-account',
    email_address: 'partner@example.com',
    display_name: 'Partner Example',
    oauth_consent: true,
    ai_read_consent: true,
    draft_only_mode: false,
    consent_timestamp: new Date().toISOString()
  },
  accounts: [
    {
      id: 'test-account',
      email_address: 'partner@example.com',
      display_name: 'Partner Example',
      oauth_consent: true,
      ai_read_consent: true,
      draft_only_mode: false,
      consent_timestamp: new Date().toISOString(),
      is_active: true
    }
  ]
}

const emailListPayload = {
  success: true,
  emails: [
    {
      id: 'demo-message',
      senderName: 'Dr. Sarah Mitchell',
      senderEmail: 'smitchell@lawfirm.com',
      subject: 'Vertragsprüfung - Henderson Fall',
      snippet: 'Bitte überprüfen Sie die beigefügte Vergleichsvereinbarung ...',
      date: new Date().toISOString(),
      unread: true
    }
  ],
  total: 1
}

test.describe('Email inbox hand-off', () => {
  test('renders inbox when backend reports connected', async ({ page }) => {
    await page.route('**/api/user/gmail/status**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(connectedStatusPayload)
      })
    })

    await page.route('**/api/email/list**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(emailListPayload)
      })
    })

    const baseUrl = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000'
    await page.goto(`${baseUrl.replace(/\/$/, '')}/email`)

    await expect(page.getByRole('heading', { name: 'E-Mail' })).toBeVisible()
    await expect(page.getByText('Vertragsprüfung - Henderson Fall')).toBeVisible()
    await expect(page.locator('.consent-card')).toHaveCount(0)
  })

  test('clears inbox state when switching to another user', async ({ page }) => {
    let statusPayload: any = { ...connectedStatusPayload }

    await page.route('**/api/user/gmail/status**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(statusPayload)
      })
    })

    await page.route('**/api/email/list**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(emailListPayload)
      })
    })

    await page.addInitScript(({ initialUser }) => {
      const listeners: Array<(event: string, session: any) => void> = []
      let currentUserId = initialUser

      // Minimal Supabase auth stub so the app can resolve the active user id
      // and react to auth state changes without hitting the real API.
      // @ts-ignore - exposed globally for the Nuxt plugin guard
      window.__ANWALTS_SUPABASE__ = {
        auth: {
          getSession: async () => ({
            data: {
              session: currentUserId
                ? { user: { id: currentUserId } }
                : null
            }
          }),
          onAuthStateChange: (callback) => {
            listeners.push(callback)
            return { data: { subscription: { unsubscribe: () => {} } } }
          }
        }
      }

      // Helper the test can call to simulate Supabase auth transitions.
      // @ts-ignore - exposed for tests
      window.__SET_SUPABASE_USER__ = (nextId) => {
        currentUserId = nextId
        const session = nextId ? { user: { id: nextId } } : null
        const event = nextId ? 'SIGNED_IN' : 'SIGNED_OUT'
        listeners.forEach((cb) => {
          try {
            cb(event, session)
          } catch (err) {
            console.warn('Auth listener error', err)
          }
        })
      }

      try {
        localStorage.setItem('supabase.auth.token', JSON.stringify({ user: { id: currentUserId } }))
      } catch (err) {
        console.warn('Failed to seed Supabase auth token', err)
      }
    }, { initialUser: 'user-a' })

    const baseUrl = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000'
    await page.goto(`${baseUrl.replace(/\/$/, '')}/email`)

    await expect(page.locator('[data-email-id="demo-message"]')).toBeVisible()

    statusPayload = {
      connected: false,
      oauth_consent: false,
      ai_read_consent: false,
      draft_only_mode: true,
      consent_timestamp: null,
      active_account: null,
      accounts: []
    }

    await page.evaluate(() => {
      localStorage.setItem('supabase.auth.token', JSON.stringify({ user: { id: 'user-b' } }))
      // @ts-ignore - provided via addInitScript above
      window.__SET_SUPABASE_USER__('user-b')
    })

    await expect(page.locator('.consent-card')).toBeVisible()
    await expect(page.locator('[data-email-id="demo-message"]')).toHaveCount(0)
  })
})
