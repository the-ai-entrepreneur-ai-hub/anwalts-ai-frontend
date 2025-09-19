// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  css: ['~/assets/css/main.css'],
  app: {
    head: {
      link: [
        { rel: 'icon', type: 'image/png', href: '/favicon.png' },
        { rel: 'apple-touch-icon', href: '/favicon.png' },
        { rel: 'shortcut icon', href: '/favicon.png' }
      ],
      script: [
        { src: 'https://cdn.tailwindcss.com' },
        // Removed problematic production-fix.js injection to prevent auto modal and conflicts
        { src: '/shared/gbutton.js' },
        // If a compatibility script is ever needed again, add it via feature-flagged plugin, not a global head script
      ]
    }
  },
  modules: [
    '@nuxt/ui',
    '@pinia/nuxt'
  ],
  runtimeConfig: {
    backendBase: process.env.BACKEND_BASE || 'http://backend_api:8000',
    GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI: process.env.GOOGLE_REDIRECT_URI,
    // Stack Auth server-side keys
    stackSecretServerKey: process.env.STACK_SECRET_SERVER_KEY,
    public: {
      apiBase: process.env.NODE_ENV === 'production' ? '/api' : (process.env.NUXT_PUBLIC_API_BASE || '/api'),
      apiEndpoints: {
        generate: '/api/ai/generate-document',
        generateSimple: '/api/ai/generate-document-simple',
        templates: '/api/templates',
        upload: '/api/files/upload',
        save: '/api/documents/save',
        exportBase: '/api/documents',
        status: '/api/documents/status'
      },
      // Stack Auth public keys
      stackProjectId: process.env.NUXT_PUBLIC_STACK_PROJECT_ID,
      stackPublishableClientKey: process.env.NUXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY,
      appUrl: process.env.NUXT_PUBLIC_APP_URL || 'https://portal-anwalts.ai'
    }
  },
  nitro: {
    envPrefix: 'GOOGLE_',
    runtimeConfig: {},
    prerender: {
      crawlLinks: false,
      // Do NOT prerender protected pages; only public landing is static
      routes: ['/'],
      ignore: ['/assistant']
    }
  },
  vite: {
    define: {
      global: 'globalThis',
    },
    optimizeDeps: {
      include: ['react', 'react-dom', 'unframer']
    },
    esbuild: {
      jsx: 'automatic'
    },
    server: {
      host: '0.0.0.0',
      port: 3000,
      strictPort: true
    }
  },
  devServer: {
    host: '0.0.0.0',
    port: 3000
  },
  build: {
    transpile: ['unframer', 'react', 'react-dom']
  },
  ssr: true,
  experimental: {
    reactivityTransform: true
  }
})
