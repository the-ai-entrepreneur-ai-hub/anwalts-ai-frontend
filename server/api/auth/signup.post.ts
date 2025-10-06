import { setSupabaseSessionCookie } from '~/server/utils/sessionCookie'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const supabase = useSupabaseServer(event)

  // Validate required fields
  const { email, password, name, law_institution, phone, address } = body

  if (!email || !password || !name || !law_institution || !phone || !address) {
    throw createError({
      statusCode: 400,
      statusMessage: 'All fields are required: email, password, name, law_institution, phone, address'
    })
  }

  // Validate email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Invalid email format'
    })
  }

  // Validate field lengths
  if (password.length < 6) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Password too short (min 6 characters)'
    })
  }

  if (name.length < 1 || name.length > 100) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Name must be 1-100 characters'
    })
  }

  if (law_institution.length < 1 || law_institution.length > 200) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Law institution must be 1-200 characters'
    })
  }

  if (phone.length < 10 || phone.length > 20) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Phone number must be 10-20 characters'
    })
  }

  if (address.length < 10 || address.length > 500) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Address must be 10-500 characters'
    })
  }

  try {
    // Sign up user with Supabase
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          name,
          law_institution,
          phone,
          address
        }
      }
    })

    if (error) {
      if (error.message.includes('already registered')) {
        throw createError({
          statusCode: 400,
          statusMessage: 'Email already registered'
        })
      }
      throw createError({
        statusCode: 500,
        statusMessage: error.message
      })
    }

    if (data.session) {
      setSupabaseSessionCookie(event, data.session)
    }

    // Fetch profile
    const { data: profile } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', data.user?.id)
      .single()

    return {
      user: {
        id: data.user?.id,
        email: data.user?.email,
        created_at: data.user?.created_at
      },
      session: {
        access_token: data.session?.access_token,
        expires_at: data.session?.expires_at,
        refresh_token: data.session?.refresh_token
      },
      profile
    }
  } catch (err: any) {
    if (err.statusCode) throw err

    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to create user profile'
    })
  }
})
