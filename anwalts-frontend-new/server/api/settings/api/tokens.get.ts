export default defineEventHandler(async (event) => {
  // TODO: Fetch real API tokens from database
  // For now, return mock data
  
  return {
    tokens: [
      {
        id: '1',
        name: 'Production API Key',
        last4: '7a9f',
        created_at: '2025-10-15T10:30:00Z',
        last_used_at: '2025-11-02T12:45:00Z',
        expires_at: '2026-10-15T10:30:00Z',
        active: true
      },
      {
        id: '2',
        name: 'Development API Key',
        last4: '3b2c',
        created_at: '2025-09-20T14:15:00Z',
        last_used_at: '2025-11-01T08:20:00Z',
        expires_at: '2026-09-20T14:15:00Z',
        active: true
      }
    ]
  }
})
