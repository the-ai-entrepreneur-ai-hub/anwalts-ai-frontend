export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  
  // TODO: Generate real API token and store in database
  // For now, return mock token
  
  const mockToken = 'anw_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
  
  return {
    token: mockToken,
    id: Math.random().toString(36).substring(2, 11),
    name: body.name || 'New API Key',
    created: new Date().toISOString(),
    expiresAt: new Date(Date.now() + (body.expires_in_days || 365) * 24 * 60 * 60 * 1000).toISOString()
  }
})
