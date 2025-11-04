export default defineEventHandler(async (event) => {
  // TODO: Fetch real data from database
  // For now, return mock data structure that matches frontend expectations
  
  return {
    kpis: [
      {
        label: 'Aktive Benutzer',
        value: '24',
        change: 12,
        iconPath: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
        iconBg: 'bg-blue-100',
        iconColor: 'text-blue-600'
      },
      {
        label: 'Dokumente',
        value: '156',
        change: 8,
        iconPath: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
        iconBg: 'bg-green-100',
        iconColor: 'text-green-600'
      },
      {
        label: 'Vorlagen',
        value: '42',
        change: 5,
        iconPath: 'M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z',
        iconBg: 'bg-purple-100',
        iconColor: 'text-purple-600'
      },
      {
        label: 'API-Aufrufe',
        value: '2.4k',
        change: 15,
        iconPath: 'M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
        iconBg: 'bg-orange-100',
        iconColor: 'text-orange-600'
      }
    ],
    systemHealth: [
      {
        name: 'API-Server',
        status: 'Betriebsbereit',
        uptime: 99.9,
        latency_ms: 45
      },
      {
        name: 'Datenbank',
        status: 'Betriebsbereit',
        uptime: 100,
        latency_ms: 12
      },
      {
        name: 'Cache-Service',
        status: 'Betriebsbereit',
        uptime: 99.8,
        latency_ms: 8
      }
    ],
    userGrowth: [
      { label: 'Jan', value: 10 },
      { label: 'Feb', value: 15 },
      { label: 'Mär', value: 18 },
      { label: 'Apr', value: 22 },
      { label: 'Mai', value: 24 },
      { label: 'Jun', value: 24 }
    ],
    apiUsage: [
      { label: 'Woche 1', value: 450 },
      { label: 'Woche 2', value: 520 },
      { label: 'Woche 3', value: 580 },
      { label: 'Woche 4', value: 650 }
    ],
    meta: {
      templates_total: 42,
      webhooks_total: 2,
      api: {
        success_rate: 98.5,
        avg_latency_ms: 245,
        total_current: 2400,
        error_calls: 35,
        last_seen: '2025-11-03T09:30:00Z'
      }
    },
    generatedAt: new Date().toISOString()
  }
})
