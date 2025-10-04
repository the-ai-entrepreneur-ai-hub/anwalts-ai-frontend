# 🚀 ANWALTS.AI Frontend - Quick Start Guide

## Prerequisites

Before starting, ensure you have:
- ✅ Node.js 18+ installed
- ✅ npm or yarn installed
- ✅ Production build completed (`npm run build`)
- ✅ Environment variables configured

## Option 1: Quick Start with Script (Recommended)

```bash
cd /root/anwalts-frontend-new
./start.sh
```

This script will:
1. Set environment variables
2. Verify the build exists
3. Start the Nuxt server on port 3000

## Option 2: Manual Start

```bash
cd /root/anwalts-frontend-new

# Export environment variables
export GOOGLE_CLIENT_ID="<YOUR_GOOGLE_CLIENT_ID>"
export GOOGLE_CLIENT_SECRET="<YOUR_GOOGLE_CLIENT_SECRET>"
export GOOGLE_REDIRECT_URI="https://portal-anwalts.ai/api/auth/oauth/google/callback"
export BACKEND_BASE="http://backend_api:8000"
export NODE_ENV="production"

# Start the server
node .output/server/index.mjs
```

## Option 3: Development Mode

```bash
cd /root/anwalts-frontend-new
npm run dev
```

## Quick Verification

After starting the server:

```bash
# Test health (should respond)
curl http://localhost:3000/

# Test Google OAuth redirect (should return 302)
curl -I http://localhost:3000/auth/google

# Test Google OAuth authorize (should return 302)
curl -I http://localhost:3000/auth/google/authorize
```

## Expected Console Output

When the server starts, you should see:
```
Listening on http://[::]:3000
```

When a user clicks the auth button, browser console shows:
```
[Auth Bridge] Initialized
```

When Google OAuth is triggered:
```
[Google OAuth] Redirecting to backend: http://backend_api:8000/auth/google/authorize
OR
[Google OAuth] Redirecting to Google: https://accounts.google.com/o/oauth2/v2/auth?client_id=...
```

## Troubleshooting

### Port 3000 already in use
```bash
# Find and kill the process
lsof -ti:3000 | xargs kill -9

# Or use a different port
PORT=3001 node .output/server/index.mjs
```

### Build not found
```bash
# Run the build first
npm ci
npm run build
```

### Environment variables not loading
```bash
# Verify they're set
echo $GOOGLE_CLIENT_ID
echo $BACKEND_BASE

# If empty, source them from a file
source .env.production  # if you have one
```

## Access Points

- **Production URL:** https://portal-anwalts.ai/
- **Local Development:** http://localhost:3000/
- **OAuth Test:** http://localhost:3000/auth/google

## Next Steps

1. ✅ Start the server
2. ✅ Verify no corner badge appears
3. ✅ Test auth modal opens
4. ✅ Test Google OAuth redirect
5. ✅ Monitor logs for errors

For detailed deployment instructions, see: **DEPLOYMENT.md**  
For all changes made, see: **CHANGES_SUMMARY.md**
