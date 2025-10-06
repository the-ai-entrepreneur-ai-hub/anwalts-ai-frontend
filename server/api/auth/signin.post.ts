import { setSupabaseSessionCookie } from '~/server/utils/sessionCookie'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const supabase = useSupabaseServer(event)

  const { email, password } = body

  if (!email || !password) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Email and password are required'
    })
  }

  try {
    // Check if account is locked
    const { data: usersData, error: adminError } = await supabase.auth.admin.listUsers({
      email,
      perPage: 1
    })

    if (adminError) {
      console.warn('Failed to load user from Supabase admin API', adminError)
    }

    const matchedUser = usersData?.users?.[0] ?? null

    if (matchedUser) {
      const { data: profile } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', matchedUser.id)
        .single()

      if (profile && profile.locked_until) {
        const lockedUntil = new Date(profile.locked_until)
        if (lockedUntil > new Date()) {
          const remainingSeconds = Math.floor((lockedUntil.getTime() - Date.now()) / 1000)
          throw createError({
            statusCode: 429,
            statusMessage: 'Account locked due to multiple failed login attempts',
            data: {
              locked_until: profile.locked_until,
              remaining_seconds: remainingSeconds
            }
          })
        }
      }
    }

    // Attempt sign in
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    })

    if (error) {
      // Increment failed login count
      if (matchedUser) {
        const { data: profile } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', matchedUser.id)
          .single()

        if (profile) {
          const newCount = (profile.failed_login_count || 0) + 1
          const updates: any = { failed_login_count: newCount }

          if (newCount >= 3) {
            const lockUntil = new Date()
            lockUntil.setMinutes(lockUntil.getMinutes() + 15)
            updates.locked_until = lockUntil.toISOString()
          }

          await supabase
            .from('profiles')
            .update(updates)
            .eq('id', matchedUser.id)

          if (newCount >= 3) {
            throw createError({
              statusCode: 429,
              statusMessage: 'Account locked due to multiple failed login attempts',
              data: {
                locked_until: updates.locked_until,
                remaining_seconds: 900
              }
            })
          }
        }
      }

      throw createError({
        statusCode: 401,
        statusMessage: 'Invalid email or password',
        data: {
          remaining_attempts: matchedUser ? Math.max(0, 3 - ((await supabase
            .from('profiles')
            .select('failed_login_count')
            .eq('id', matchedUser.id)
            .single()
          ).data?.failed_login_count || 0) - 1) : 3
        }
      })
    }

    // Reset failed login count on successful login
    if (data.user) {
      await supabase
        .from('profiles')
        .update({
          failed_login_count: 0,
          locked_until: null
        })
        .eq('id', data.user.id)

      // Fetch profile
      const { data: profile } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', data.user.id)
        .single()

      if (data.session) {
        setSupabaseSessionCookie(event, data.session)
      }

      return {
        user: {
          id: data.user.id,
          email: data.user.email
        },
        session: {
          access_token: data.session?.access_token,
          expires_at: data.session?.expires_at,
          refresh_token: data.session?.refresh_token
        },
        profile
      }
    }

    throw createError({
      statusCode: 500,
      statusMessage: 'Login failed'
    })
  } catch (err: any) {
    if (err.statusCode) throw err

    throw createError({
      statusCode: 500,
      statusMessage: err.message || 'Internal server error'
    })
  }
})
