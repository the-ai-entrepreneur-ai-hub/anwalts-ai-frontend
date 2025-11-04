export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  const body = await readBody(event)
  
  // TODO: Update webhook in database
  
  return {
    success: true,
    webhook: {
      id,
      ...body,
      updated: new Date().toISOString()
    }
  }
})
