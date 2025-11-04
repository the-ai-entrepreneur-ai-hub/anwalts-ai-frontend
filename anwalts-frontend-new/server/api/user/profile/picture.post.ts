import { readMultipartFormData } from 'h3'
import { writeFile, mkdir } from 'fs/promises'
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

    // Parse multipart form data
    const formData = await readMultipartFormData(event)

    if (!formData || formData.length === 0) {
      throw createError({
        statusCode: 400,
        statusMessage: 'No file uploaded'
      })
    }

    const fileEntry = formData.find(item => item.name === 'file')
    
    if (!fileEntry || !fileEntry.data) {
      throw createError({
        statusCode: 400,
        statusMessage: 'No file in form data'
      })
    }

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp']
    if (!allowedTypes.includes(fileEntry.type || '')) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Invalid file type. Only JPEG, PNG, and WebP are allowed.'
      })
    }

    // Validate file size (2MB)
    const maxSize = 2 * 1024 * 1024
    if (fileEntry.data.length > maxSize) {
      throw createError({
        statusCode: 400,
        statusMessage: 'File too large. Maximum size is 2MB.'
      })
    }

    // Create uploads directory if it doesn't exist
    const uploadsDir = join(process.cwd(), 'public', 'uploads', 'avatars')
    if (!existsSync(uploadsDir)) {
      await mkdir(uploadsDir, { recursive: true })
    }

    // Generate filename
    const ext = fileEntry.type === 'image/jpeg' ? 'jpg' : fileEntry.type === 'image/png' ? 'png' : 'webp'
    const identifier = userId || userEmail?.split('@')[0] || 'user'
    const filename = `${identifier}-${Date.now()}.${ext}`
    const filepath = join(uploadsDir, filename)

    // Save file
    await writeFile(filepath, fileEntry.data)

    // Generate public URL
    const profilePictureUrl = `/uploads/avatars/${filename}`

    // Store in cookie for persistence
    setCookie(event, 'profile_picture', profilePictureUrl, {
      httpOnly: false,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 365 // 1 year
    })

    return {
      profile_picture: profilePictureUrl
    }
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || 'Failed to upload profile picture'
    })
  }
})

