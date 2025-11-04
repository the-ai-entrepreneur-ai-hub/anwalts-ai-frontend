export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  const body = await readBody(event)
  
  // TODO: Toggle user active status in database
  
  return {
    success: true,
    user: {
      id,
      active: body.active,
      updated: new Date().toISOString()
    }
  }
})
