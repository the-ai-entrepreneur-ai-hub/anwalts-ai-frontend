import { defineConfig } from 'vitest/config'
import path from 'node:path'

export default defineConfig({
  test: {
    include: ['test/**/*.spec.ts', 'tests/unit/**/*.spec.ts'],
    exclude: ['tests/e2e/**']
  },
  resolve: {
    alias: {
      '~': path.resolve(__dirname),
    },
  },
})
