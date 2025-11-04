export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  
  // TODO: Delete token from database
  
  return {
    success: true,
    message: 'Token deleted successfully'
  }
})
