export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  
  // TODO: Test webhook by sending test payload
  
  return {
    success: true,
    status: 200,
    responseTime: 145,
    message: 'Webhook test successful'
  }
})
