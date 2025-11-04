export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  
  // TODO: Create webhook in database
  
  return {
    success: true,
    webhook: {
      id: Math.random().toString(36).substring(2, 11),
      name: body.name,
      url: body.url,
      events: body.events || [],
      active: body.active !== false,
      created: new Date().toISOString()
    }
  }
})
