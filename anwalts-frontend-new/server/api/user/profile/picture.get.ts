export default defineEventHandler(async (event) => {
  try {
    // Get user from session/cookie
    const userId = getCookie(event, 'user_id')
    const userEmail = getCookie(event, 'user_email')
    
    if (!userId && !userEmail) {
      throw createError({
        statusCode: 401,
        statusMessage: 'Unauthorized'
      })
    }

    // Check if profile picture exists in user storage
    // For now, we'll check localStorage on client side, but return from cookies if available
    const profilePicture = getCookie(event, 'profile_picture')
    
    return {
      profile_picture: profilePicture || null
    }
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || 'Failed to fetch profile picture'
    })
  }
})

