export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    const entry = {
      ts: new Date().toISOString(),
      ip: getHeader(event, 'x-forwarded-for') || getHeader(event, 'x-real-ip') || 'unknown',
      ...body
    }
    console.info('[client-debug]', JSON.stringify(entry))
    return { ok: true }
  } catch (err) {
    console.error('[client-debug-error]', err)
    return { ok: false }
  }
})
