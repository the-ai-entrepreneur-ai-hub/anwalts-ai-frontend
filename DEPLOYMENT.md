# Deployment Guide - ANWALTS.AI Frontend

## Changes Summary

This deployment includes the following critical updates:

### 1. **Removed Framer Corner Badge**
   - Added CSS and inline JavaScript to completely hide and remove `#__framer-badge-container`
   - Prevents any corner/bottom-left popup from appearing
   - MutationObserver watches for badge re-insertion and removes it

### 2. **Single Centered Auth Modal**
   - Consolidated to one auth modal: `GlassmorphismAuthModal.vue`
   - Deleted duplicate modal files (if they existed):
     - `public/shared/landing-auth-modal.js`
     - `public/shared/fix-framer-modal.js`
   - Auth modal is controlled by `useAuthModal` composable

### 3. **Fixed Google OAuth Flow**
   - Created `/auth/google` redirect route
   - Created `/auth/google/authorize` OAuth handler
   - Supports three strategies:
     1. Redirect to backend OAuth endpoint (preferred)
     2. Direct Google OAuth with client credentials
     3. Fallback to home with error parameter

### 4. **PostMessage Bridge**
   - iframe communicates with parent via `postMessage`
   - Parent window listens for `ANWALTS_OPEN_AUTH` and `ANWALTS_CLOSE_AUTH` events
   - iframe never opens its own modal (returns immediately after posting message)

## Environment Variables

Before deploying, ensure these environment variables are set in your production environment:

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=<YOUR_GOOGLE_CLIENT_ID>
GOOGLE_CLIENT_SECRET=<YOUR_GOOGLE_CLIENT_SECRET>
GOOGLE_REDIRECT_URI=https://portal-anwalts.ai/api/auth/oauth/google/callback

# Backend API URL (for OAuth delegation)
BACKEND_BASE=http://backend_api:8000

# Optional: CORS and Session Configuration
CORS_ORIGIN=https://portal-anwalts.ai
SESSION_COOKIE_NAME=anwalts_session
NODE_ENV=production
```

## Deployment Steps

### Option 1: Systemd Service

```bash
# 1. Navigate to project directory
cd /root/anwalts-frontend-new

# 2. Set environment variables (add to /etc/environment or service file)
sudo nano /etc/systemd/system/anwalts-frontend.service

# Add environment variables to the [Service] section:
# Environment="GOOGLE_CLIENT_ID=<YOUR_GOOGLE_CLIENT_ID>"
# Environment="GOOGLE_CLIENT_SECRET=<YOUR_GOOGLE_CLIENT_SECRET>"
# Environment="GOOGLE_REDIRECT_URI=https://portal-anwalts.ai/api/auth/oauth/google/callback"
# Environment="BACKEND_BASE=http://backend_api:8000"

# 3. Restart the service
sudo systemctl daemon-reload
sudo systemctl restart anwalts-frontend

# 4. Check status
sudo systemctl status anwalts-frontend

# 5. View logs
sudo journalctl -u anwalts-frontend -f
```

### Option 2: PM2

```bash
# 1. Navigate to project directory
cd /root/anwalts-frontend-new

# 2. Create PM2 ecosystem file
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'anwalts-frontend',
    script: './.output/server/index.mjs',
    env: {
      NODE_ENV: 'production',
      GOOGLE_CLIENT_ID: '<YOUR_GOOGLE_CLIENT_ID>',
      GOOGLE_CLIENT_SECRET: '<YOUR_GOOGLE_CLIENT_SECRET>',
      GOOGLE_REDIRECT_URI: 'https://portal-anwalts.ai/api/auth/oauth/google/callback',
      BACKEND_BASE: 'http://backend_api:8000'
    }
  }]
}
EOF

# 3. Restart with PM2
pm2 restart anwalts-frontend

# Or if not yet started:
pm2 start ecosystem.config.js

# 4. Save PM2 configuration
pm2 save

# 5. View logs
pm2 logs anwalts-frontend
```

### Option 3: Docker

```bash
# 1. Navigate to project directory
cd /root/anwalts-frontend-new

# 2. Update docker-compose.yml or Dockerfile with environment variables
# Add to your docker-compose.yml:
#
# services:
#   nuxt:
#     environment:
#       - GOOGLE_CLIENT_ID=<YOUR_GOOGLE_CLIENT_ID>
#       - GOOGLE_CLIENT_SECRET=<YOUR_GOOGLE_CLIENT_SECRET>
#       - GOOGLE_REDIRECT_URI=https://portal-anwalts.ai/api/auth/oauth/google/callback
#       - BACKEND_BASE=http://backend_api:8000

# 3. Rebuild and restart
docker compose build nuxt
docker compose up -d nuxt

# 4. View logs
docker compose logs -f nuxt
```

### Option 4: Direct Node.js

```bash
# 1. Navigate to project directory
cd /root/anwalts-frontend-new

# 2. Export environment variables
export GOOGLE_CLIENT_ID="<YOUR_GOOGLE_CLIENT_ID>"
export GOOGLE_CLIENT_SECRET="<YOUR_GOOGLE_CLIENT_SECRET>"
export GOOGLE_REDIRECT_URI="https://portal-anwalts.ai/api/auth/oauth/google/callback"
export BACKEND_BASE="http://backend_api:8000"
export NODE_ENV="production"

# 3. Run the server
node .output/server/index.mjs

# Or with a process manager like nohup:
nohup node .output/server/index.mjs > server.log 2>&1 &
```

## CDN Cache Purging

If you're using a CDN like Cloudflare:

```bash
# Purge cache for all static assets
curl -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/purge_cache" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"files":["https://portal-anwalts.ai/*"]}'

# Or purge everything:
curl -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/purge_cache" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'
```

## Verification Steps

### 1. Test Corner Badge Removal
```bash
# Open the site and check for corner popup
# Expected: No corner/bottom-left widget visible
open https://portal-anwalts.ai/
```

### 2. Test Single Auth Modal
```bash
# Click "Registrieren/Anmelden" button in landing iframe
# Expected: One centered modal appears on parent page
# Expected: No duplicate modals
```

### 3. Test Google OAuth Redirect
```bash
# Test the redirect chain
curl -I https://portal-anwalts.ai/auth/google

# Expected output:
# HTTP/1.1 302 Found
# Location: /auth/google/authorize

curl -I https://portal-anwalts.ai/auth/google/authorize

# Expected output:
# HTTP/1.1 302 Found
# Location: http://backend_api:8000/auth/google/authorize
# OR
# Location: https://accounts.google.com/o/oauth2/v2/auth?client_id=...
```

### 4. Test UI Flow
1. Navigate to `https://portal-anwalts.ai/`
2. Confirm no corner popup appears
3. Click "Registrieren/Anmelden" in the iframe
4. Confirm single centered modal opens
5. Click "Mit Google fortfahren"
6. Confirm redirect to Google consent screen (no 404)
7. Test navigation to `/dashboard` while signed-out
8. Confirm parent modal opens (no iframe popup)

## Monitoring

```bash
# Check server logs
sudo journalctl -u anwalts-frontend -f

# Or with PM2
pm2 logs anwalts-frontend

# Or with Docker
docker compose logs -f nuxt

# Check for errors in browser console
# Open DevTools → Console → Look for Auth Bridge messages
```

## Rollback Instructions

If you need to rollback:

```bash
# 1. Navigate to project directory
cd /root/anwalts-frontend-new

# 2. Checkout previous commit
git log --oneline -10  # Find the previous commit hash
git checkout <previous-commit-hash>

# 3. Rebuild
npm ci
npm run build

# 4. Restart service
sudo systemctl restart anwalts-frontend
# OR
pm2 restart anwalts-frontend
# OR
docker compose restart nuxt
```

## Troubleshooting

### Issue: Google OAuth returns 404

**Solution:** Check that:
1. Environment variables are set correctly
2. Server routes are built (check `.output/server/chunks/routes/auth/`)
3. Server restarted after build

```bash
# Verify routes exist
ls -la /root/anwalts-frontend-new/.output/server/chunks/routes/auth/

# Should show:
# google.get.mjs
# google/authorize.get.mjs
```

### Issue: Modal doesn't open

**Solution:** Check browser console for:
1. `[Auth Bridge] Initialized` message
2. PostMessage events being sent
3. Window object has `__anwaltsAuthModal` registered

```javascript
// In browser console:
console.log(window.__anwaltsAuthModal)
// Should show: { isOpen: ref, open: fn, close: fn }
```

### Issue: Corner badge still appears

**Solution:** 
1. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
2. Clear browser cache
3. Check that `page.html` includes the badge removal script
4. Inspect DOM for `#__framer-badge-container` (should not exist)

## Files Modified

- ✅ Created: `public/page.html`
- ✅ Created: `public/shared/auth-modal-bridge.js`
- ✅ Created: `public/shared/anwalts-auth.css`
- ✅ Created: `public/shared/gbutton.js`
- ✅ Modified: `pages/index.vue`
- ✅ Created: `server/routes/auth/google.get.ts`
- ✅ Created: `server/routes/auth/google/authorize.get.ts`

## Build Output Location

```
/root/anwalts-frontend-new/.output/
├── public/          # Static assets
├── server/          # Server bundle
│   ├── index.mjs    # Entry point
│   └── chunks/
│       └── routes/
│           └── auth/
│               ├── google.get.mjs
│               └── google/
│                   └── authorize.get.mjs
└── nitro.json       # Build metadata
```

## Success Criteria

- ✅ No corner/bottom-left Framer badge visible
- ✅ Single centered auth modal triggered from CTAs
- ✅ "Mit Google fortfahren" redirects correctly (no 404)
- ✅ OAuth flow completes successfully
- ✅ Production build deployed and running
- ✅ All environment variables configured

## Support

For issues or questions:
1. Check server logs for errors
2. Check browser console for client-side errors
3. Verify environment variables are set
4. Test OAuth endpoints with curl
5. Review this deployment guide

---

**Deployment Date:** 2025-10-03
**Build Version:** Nuxt 4.1.2 / Nitro 2.12.6
**Status:** ✅ Ready for Production
