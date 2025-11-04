# Implementation Tasks

## 1. Analysis
- [x] 1.1 Identify email section navigation visibility issue
- [x] 1.2 Compare email.vue navigation CSS with templates.vue and assistant.vue
- [x] 1.3 Locate problematic mobile-responsive CSS in email.vue

## 2. Code Changes
- [x] 2.1 Remove `position: fixed` and off-screen positioning from `.email-nav-tabs` mobile styles
- [x] 2.2 Replace hidden mobile drawer with flex-wrap layout for navigation tabs
- [x] 2.3 Remove `.email-nav-tabs.mobile-open` state handling
- [x] 2.4 Hide mobile menu close button (`.mobile-menu-close { display: none; }`)
- [x] 2.5 Adjust `.nav-tabs-inner` to use `flex-wrap: wrap` and full width
- [x] 2.6 Update `.nav-tab` and `.labels-dropdown-container` to use `flex: 0 1 auto`

## 3. Build & Testing
- [x] 3.1 Build Nuxt application: `npm run build` in `/root/anwalts-frontend-new`
- [x] 3.2 Rebuild Docker frontend container: `docker-compose build --no-cache frontend`
- [x] 3.3 Verify build completed without errors

## 4. Deployment
- [x] 4.1 Stop existing frontend container: `docker stop anwalts_frontend && docker rm anwalts_frontend`
- [x] 4.2 Deploy new frontend container with updated image
- [x] 4.3 Reload nginx configuration: `sudo nginx -s reload`
- [x] 4.4 Verify container health status
- [x] 4.5 Test local endpoint: `curl http://localhost:3000/` returns 200
- [x] 4.6 Test production endpoint: `curl https://portal-anwalts.ai/email` returns 200

## 5. Verification
- [x] 5.1 Confirm navigation buttons visible on desktop
- [x] 5.2 Confirm navigation buttons visible on tablet viewport (responsive testing)
- [x] 5.3 Confirm navigation buttons visible on mobile viewport
- [x] 5.4 Verify no JavaScript errors in browser console
- [x] 5.5 Verify deployment is live on production site

## 6. Documentation
- [x] 6.1 Create OpenSpec change proposal
- [x] 6.2 Document changes in proposal.md
- [x] 6.3 Document implementation steps in tasks.md
