export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  
  // TODO: Save preferences to database
  
  return {
    success: true,
    preferences: body,
    saved: new Date().toISOString()
  }
})
