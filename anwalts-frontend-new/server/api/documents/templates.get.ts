import { defineEventHandler } from 'h3'
import { fetchTemplatesFromBackend } from '~/server/utils/documentsCatalog'

export default defineEventHandler(async (event) => {
  return await fetchTemplatesFromBackend(event)
})
