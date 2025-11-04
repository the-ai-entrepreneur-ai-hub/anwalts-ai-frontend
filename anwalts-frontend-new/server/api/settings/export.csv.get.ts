export default defineEventHandler(async (event) => {
  // TODO: Generate real CSV export from database
  
  const csv = `Email,Name,Role,Status,Joined
angelageneralao.1997@gmail.com,Angela Generalao,admin,active,2025-09-15
test.reg.e2e+20251026@anwalts.ai,Test Admin,admin,active,2025-10-26
user@example.com,Demo User,user,active,2025-10-01`
  
  setHeader(event, 'Content-Type', 'text/csv')
  setHeader(event, 'Content-Disposition', 'attachment; filename="users-export.csv"')
  
  return csv
})
