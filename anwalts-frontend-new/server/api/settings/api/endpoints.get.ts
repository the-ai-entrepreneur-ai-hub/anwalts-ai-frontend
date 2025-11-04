export default defineEventHandler(async (event) => {
  // TODO: Fetch real API endpoint metrics from database
  
  return {
    metrics: [
      {
        method: 'POST',
        path: '/api/ai/complete',
        call_count: 1240,
        avg_latency_ms: 320,
        peak_per_minute: 45,
        error_count: 12,
        last_called: '2025-11-02T12:45:00Z'
      },
      {
        method: 'POST',
        path: '/api/documents/process',
        call_count: 856,
        avg_latency_ms: 450,
        peak_per_minute: 28,
        error_count: 8,
        last_called: '2025-11-02T11:30:00Z'
      },
      {
        method: 'GET',
        path: '/api/templates',
        call_count: 423,
        avg_latency_ms: 120,
        peak_per_minute: 15,
        error_count: 2,
        last_called: '2025-11-02T10:15:00Z'
      },
      {
        method: 'GET',
        path: '/api/email/list',
        call_count: 312,
        avg_latency_ms: 280,
        peak_per_minute: 12,
        error_count: 5,
        last_called: '2025-11-02T09:20:00Z'
      }
    ]
  }
})
