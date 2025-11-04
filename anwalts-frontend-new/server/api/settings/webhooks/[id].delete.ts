export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  
  // TODO: Delete webhook from database
  
  return {
    success: true,
    message: 'Webhook deleted successfully'
  }
})
