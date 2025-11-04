export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  const body = await readBody(event)
  
  // TODO: Update user role in database
  
  return {
    success: true,
    user: {
      id,
      role: body.role,
      updated: new Date().toISOString()
    }
  }
})
