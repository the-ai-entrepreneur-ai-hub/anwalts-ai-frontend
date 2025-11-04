export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  
  // TODO: Fetch real users from database with search/filter
  
  return {
    users: [
      {
        id: '1',
        email: 'angelageneralao.1997@gmail.com',
        name: 'Angela Generalao',
        role: 'admin',
        is_active: true,
        joined_at: '2025-09-15T10:00:00Z',
        last_activity: '2025-11-02T14:30:00Z'
      },
      {
        id: '2',
        email: 'test.reg.e2e+20251026@anwalts.ai',
        name: 'Test Admin',
        role: 'admin',
        is_active: true,
        joined_at: '2025-10-26T12:00:00Z',
        last_activity: '2025-11-01T09:15:00Z'
      },
      {
        id: '3',
        email: 'user@example.com',
        name: 'Demo User',
        role: 'staff',
        is_active: true,
        joined_at: '2025-10-01T14:20:00Z',
        last_activity: '2025-11-02T08:45:00Z'
      },
      {
        id: '4',
        email: 'viewer@example.com',
        name: 'Read Only User',
        role: 'viewer',
        is_active: true,
        joined_at: '2025-10-05T16:30:00Z',
        last_activity: '2025-11-01T18:20:00Z'
      }
    ],
    total: 4,
    page: 1,
    pageSize: 20
  }
})
