export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const supabase = useSupabaseServer(event)

  // Get session from cookie
  const sessionCookie = getCookie(event, 'supabase-session')
  if (!sessionCookie) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Authentication required'
    })
  }

  let session
  try {
    session = JSON.parse(sessionCookie)
  } catch {
    throw createError({
      statusCode: 401,
      statusMessage: 'Invalid session'
    })
  }

  // Verify session
  const { data: { user }, error: authError } = await supabase.auth.getUser(session.access_token)

  if (authError || !user) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Invalid or expired session'
    })
  }

  // Validate update fields
  const allowedFields = ['name', 'law_institution', 'phone', 'address']
  const updates: any = {}

  for (const field of allowedFields) {
    if (body[field] !== undefined) {
      updates[field] = body[field]
    }
  }

  if (Object.keys(updates).length === 0) {
    throw createError({
      statusCode: 400,
      statusMessage: 'No valid fields to update'
    })
  }

  // Validate field constraints
  if (updates.name !== undefined && (updates.name.length < 1 || updates.name.length > 100)) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Name must be 1-100 characters'
    })
  }

  if (updates.law_institution !== undefined && (updates.law_institution.length < 1 || updates.law_institution.length > 200)) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Law institution must be 1-200 characters'
    })
  }

  if (updates.phone !== undefined && (updates.phone.length < 10 || updates.phone.length > 20)) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Phone must be 10-20 characters'
    })
  }

  if (updates.address !== undefined && (updates.address.length < 10 || updates.address.length > 500)) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Address must be 10-500 characters'
    })
  }

  try {
    // Update profile
    const { data, error } = await supabase
      .from('profiles')
      .update(updates)
      .eq('id', user.id)
      .select()
      .single()

    if (error) {
      throw createError({
        statusCode: 500,
        statusMessage: 'Failed to update profile'
      })
    }

    return {
      success: true,
      profile: data
    }
  } catch (err: any) {
    if (err.statusCode) throw err

    throw createError({
      statusCode: 500,
      statusMessage: err.message || 'Profile update failed'
    })
  }
})
