import { unlink } from 'fs/promises'
import { join } from 'path'
import { existsSync } from 'fs'

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

    // Get current profile picture URL from cookie
    const profilePicture = getCookie(event, 'profile_picture')
    
    if (profilePicture) {
      // Extract filename from URL
      const filename = profilePicture.split('/').pop()
      if (filename) {
        const filepath = join(process.cwd(), 'public', 'uploads', 'avatars', filename)
        
        // Delete file if it exists
        if (existsSync(filepath)) {
          try {
            await unlink(filepath)
          } catch (error) {
            console.error('Failed to delete profile picture file:', error)
          }
        }
      }
    }

    // Clear profile picture cookie
    deleteCookie(event, 'profile_picture')

    return {
      success: true,
      message: 'Profile picture removed successfully'
    }
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || 'Failed to delete profile picture'
    })
  }
})

