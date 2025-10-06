import { buildBackendUrl } from '~/server/utils/backend'
import { readSupabaseSessionCookie } from '~/server/utils/sessionCookie'

type BackendSummaryResponse = {
  new_cases?: number
  documents_total?: number
  documents_recent?: number
  emails_total?: number
  emails_recent?: number
  next_deadline?: string | null
  generated_at?: string
}

export default defineEventHandler(async (event) => {
  const supabase = useSupabaseServer(event)
  const sessionCookie = readSupabaseSessionCookie(event)
  const config = useRuntimeConfig()

  if (!sessionCookie?.access_token) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Authentication required'
    })
  }

  const warnings: string[] = []

  try {
    const { data: userData, error: userError } = await supabase.auth.getUser(sessionCookie.access_token)

    if (userError || !userData.user) {
      throw createError({
        statusCode: 401,
        statusMessage: 'Invalid session'
      })
    }

    const user = userData.user

    let profile: Record<string, any> | null = null
    try {
      const { data: profileData, error: profileError } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', user.id)
        .single()

      if (profileError) {
        warnings.push('Profil konnte nicht geladen werden.')
      }

      profile = profileData ?? null
    } catch (err: any) {
      warnings.push(`Profilabfrage fehlgeschlagen: ${err?.message ?? 'Unbekannter Fehler'}`)
    }

    let backendSummary: BackendSummaryResponse | null = null
    const serviceKey = (config.dashboardServiceKey as string | undefined)?.trim()

    if (serviceKey) {
      const backendUrl = buildBackendUrl(event, `/internal/dashboard-summary/${encodeURIComponent(user.id)}`)
      try {
        backendSummary = await $fetch<BackendSummaryResponse>(backendUrl, {
          headers: {
            Accept: 'application/json',
            'x-service-key': serviceKey
          }
        })
      } catch (err: any) {
        console.error('Dashboard backend summary error', err)
        warnings.push('Dashboard-Metriken konnten nicht vom Backend geladen werden.')
      }
    } else {
      warnings.push('DASHBOARD_SERVICE_KEY ist nicht konfiguriert; es werden Placeholder-Werte angezeigt.')
    }

    const stats = {
      newCases: backendSummary?.new_cases ?? backendSummary?.documents_recent ?? 0,
      documents: backendSummary?.documents_total ?? 0,
      emails: backendSummary?.emails_total ?? 0,
      nextDeadline: backendSummary?.next_deadline ?? null
    }

    return {
      stats,
      warnings: warnings.length ? warnings : undefined,
      profile: profile ?? null,
      user: {
        id: user.id,
        email: user.email,
        last_sign_in_at: user.last_sign_in_at,
        user_metadata: user.user_metadata ?? {}
      }
    }
  } catch (error: any) {
    if (error.statusCode) {
      throw error
    }

    console.error('Dashboard summary failure', error)

    throw createError({
      statusCode: 500,
      statusMessage: 'Dashboard summary unavailable'
    })
  }
})
