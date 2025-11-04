export default defineEventHandler(async (event) => {
  // TODO: Generate real JSON export from database
  
  const data = {
    exportDate: new Date().toISOString(),
    users: [
      {
        email: 'angelageneralao.1997@gmail.com',
        name: 'Angela Generalao',
        role: 'admin',
        status: 'active',
        joined: '2025-09-15T10:00:00Z'
      },
      {
        email: 'test.reg.e2e+20251026@anwalts.ai',
        name: 'Test Admin',
        role: 'admin',
        status: 'active',
        joined: '2025-10-26T12:00:00Z'
      },
      {
        email: 'user@example.com',
        name: 'Demo User',
        role: 'user',
        status: 'active',
        joined: '2025-10-01T14:20:00Z'
      }
    ],
    statistics: {
      totalUsers: 3,
      activeUsers: 3,
      totalDocuments: 156,
      totalTemplates: 42
    }
  }
  
  setHeader(event, 'Content-Type', 'application/json')
  setHeader(event, 'Content-Disposition', 'attachment; filename="data-export.json"')
  
  return data
})
