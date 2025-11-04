export default defineEventHandler(async (event) => {
  try {
    // Get user data from cookies
    const userId = getCookie(event, 'user_id')
    const userEmail = getCookie(event, 'user_email')
    const userName = getCookie(event, 'user_name')
    const userRole = getCookie(event, 'user_role')
    const profilePicture = getCookie(event, 'profile_picture')
    
    const token = getCookie(event, 'auth_token') || 
                  getCookie(event, 'anwalts_auth_token') ||
                  getCookie(event, 'sat')
    
    if (!token && !userId && !userEmail) {
      throw createError({
        statusCode: 401,
        statusMessage: 'Unauthorized'
      })
    }

    // Build user object from cookies
    const user = {
      id: userId || null,
      email: userEmail || null,
      name: userName || userEmail || null,
      role: userRole || 'user',
      profile_picture: profilePicture || null
    }

    return user
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || 'Failed to fetch user data'
    })
  }
})

