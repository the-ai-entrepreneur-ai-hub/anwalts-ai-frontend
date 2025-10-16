// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  css: ['~/assets/css/tailwind.css', '~/assets/css/main.css'],
  app: {
    head: {
      link: [
        { rel: 'icon', type: 'image/png', href: '/favicon.png' },
        { rel: 'apple-touch-icon', href: '/favicon.png' },
        { rel: 'shortcut icon', href: '/favicon.png' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap' }
      ],
      script: [
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
    backendBase: process.env.BACKEND_BASE || 'http://backend:8000',
    dashboardServiceKey: process.env.DASHBOARD_SERVICE_KEY,
    GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI: process.env.GOOGLE_REDIRECT_URI,
    supabaseServiceKey: process.env.SUPABASE_SERVICE_ROLE_KEY,
    public: {
      supabaseUrl: process.env.SUPABASE_URL,
      supabaseKey: process.env.SUPABASE_ANON_KEY,
      apiBase: process.env.NODE_ENV === 'production' ? '/api' : (process.env.NUXT_PUBLIC_API_BASE || '/api'),
      apiEndpoints: {
        generate: '/api/ai/generate-document',
        generateSimple: '/api/ai/generate-document-simple',
        templates: '/api/templates',
        upload: '/api/files/upload',
        save: '/api/documents/save',
        exportBase: '/api/documents',
        status: '/api/documents/status'
      }
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
      include: ['react', 'react-dom']
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
    transpile: ['unframer']
  },
  ssr: true,
  experimental: {
    reactivityTransform: true
  },
  routeRules: {
    // Force server-side handling for OAuth callback (bypass client-side router)
    '/api/auth/google/callback': { ssr: true }
  }
})
