export default defineEventHandler(async (event) => {
  // TODO: Fetch real webhooks from database
  
  return {
    webhooks: [
      {
        id: '1',
        name: 'Document Created',
        url: 'https://example.com/webhooks/document-created',
        events: ['document.created', 'document.updated'],
        is_active: true,
        has_secret: true,
        created_at: '2025-10-15T10:30:00Z',
        recent_logs: [
          { id: '1', status: 200, latency_ms: 125, timestamp: '2025-11-02T12:30:00Z' },
          { id: '2', status: 200, latency_ms: 132, timestamp: '2025-11-02T11:15:00Z' },
          { id: '3', status: 500, latency_ms: 89, timestamp: '2025-11-02T10:45:00Z' }
        ]
      },
      {
        id: '2',
        name: 'User Registration',
        url: 'https://example.com/webhooks/user-registered',
        events: ['user.registered'],
        is_active: true,
        has_secret: false,
        created_at: '2025-10-20T14:15:00Z',
        recent_logs: [
          { id: '4', status: 200, latency_ms: 98, timestamp: '2025-11-01T15:20:00Z' },
          { id: '5', status: 200, latency_ms: 102, timestamp: '2025-11-01T14:10:00Z' }
        ]
      }
    ]
  }
})
