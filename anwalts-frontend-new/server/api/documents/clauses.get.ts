import { defineEventHandler } from 'h3'
import { fetchClausesFromBackend } from '~/server/utils/documentsCatalog'

export default defineEventHandler(async (event) => {
  return await fetchClausesFromBackend(event)
})
