# Google OAuth Authentication - Complete Solution

## Problem
The error "Page not found: /api/auth/google/callback" was occurring because of routing conflicts between the Nuxt frontend and FastAPI backend.

## Solution Implemented

### 1. **Created OAuth Handlers in Nuxt**
- `/server/api/auth/google.get.ts` - Initiates Google OAuth flow
- `/server/api/auth/google/callback.get.ts` - Handles OAuth callback
- Both handlers support fallback to backend OAuth if Supabase is not configured

### 2. **Supabase Integration**
- Created Supabase client plugin at `/plugins/supabase.client.ts`
- Configured auth state management and session persistence
- Supports PKCE flow for enhanced security

### 3. **Google Sign-In Component**
- Created reusable `GoogleSignInButton.vue` component
- Handles both Supabase and backend OAuth flows
- Includes error handling and loading states

### 4. **API Proxy Middleware**
- Created `/server/middleware/api-proxy.ts` to route API calls correctly
- Ensures OAuth routes are handled by the appropriate service

### 5. **Production Configuration**
- Built production Nuxt application
- Configured nginx for proper routing
- Set up systemd services for automatic startup

## Current Architecture

```
User Browser
    ↓
https://portal-anwalts.ai
    ↓
Nginx (port 443/80)
    ↓
    ├── /api/auth/* → Nuxt Server (port 3000)
    │                    ↓
    │               OAuth Handlers
    │                    ↓
    │          ┌──────────┴──────────┐
    │          ↓                      ↓
    │    Supabase Auth          Backend API
    │    (if enabled)           (port 8000)
    │
    └── /* → Nuxt App (port 3000)
```

## OAuth Flow

1. User clicks "Sign in with Google" button
2. Request goes to `/api/auth/google`
3. Nuxt handler checks configuration:
   - If Supabase enabled → Use Supabase OAuth
   - Otherwise → Redirect to backend OAuth
4. Google authentication occurs
5. Callback to `/api/auth/google/callback`
6. Handler processes the authentication:
   - Exchanges code for session
   - Sets authentication cookies
   - Redirects to dashboard

## Environment Variables

```bash
# Supabase Configuration
SUPABASE_URL=https://portal-anwalts.ai/supabase
SUPABASE_ANON_KEY=sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH
SUPABASE_SERVICE_ROLE_KEY=<REDACTED_SUPABASE_SERVICE_ROLE_KEY>

# Google OAuth
GOOGLE_CLIENT_ID=<REDACTED_GOOGLE_CLIENT_ID>
GOOGLE_CLIENT_SECRET=<REDACTED_GOOGLE_SECRET>
GOOGLE_REDIRECT_URI=https://portal-anwalts.ai/api/auth/google/callback

# Optional: Force Supabase Auth
USE_SUPABASE_AUTH=false  # Set to true to use Supabase exclusively
```

## Files Modified/Created

### New Files
- `/root/anwalts-frontend-new/server/api/auth/google.get.ts`
- `/root/anwalts-frontend-new/server/api/auth/google/callback.get.ts`
- `/root/anwalts-frontend-new/plugins/supabase.client.ts`
- `/root/anwalts-frontend-new/components/GoogleSignInButton.vue`
- `/root/anwalts-frontend-new/server/middleware/api-proxy.ts`
- `/etc/nginx/sites-available/anwalts-portal`
- `/etc/systemd/system/anwalts-backend.service`
- `/etc/systemd/system/anwalts-frontend.service`

### Backed Up Files
- `/root/anwalts-frontend-new/server/api/auth/google/callback.get.ts.backup`
- `/root/anwalts-frontend-new/server/api/auth/oauth/google/callback.get.ts.backup`

## Testing the Solution

### Local Testing
```bash
# Test backend OAuth endpoint
curl http://localhost:8000/auth/google/callback?code=test
# Expected: {"detail":"OAuth exchange failed"} (correct error for invalid code)

# Test frontend OAuth endpoint
curl http://localhost:3000/api/auth/google
# Expected: 302 redirect to Google OAuth
```

### Production Testing
1. Navigate to https://portal-anwalts.ai
2. Click "Sign in with Google" button
3. Complete Google authentication
4. Verify redirect to dashboard

## Troubleshooting

### If OAuth still fails:

1. **Check Services**
   ```bash
   systemctl status anwalts-backend
   systemctl status anwalts-frontend
   systemctl status nginx
   ```

2. **Check Logs**
   ```bash
   tail -f /tmp/nuxt-prod.log
   journalctl -u anwalts-backend -f
   journalctl -u nginx -f
   ```

3. **Verify Environment Variables**
   - Ensure all OAuth credentials are correct
   - Check Google Cloud Console for redirect URI configuration
   - Verify Supabase project settings if using Supabase

4. **Clear Browser Cache**
   - Clear cookies and local storage for portal-anwalts.ai
   - Try incognito/private browsing mode

## Next Steps

1. **Enable Supabase Auth** (Recommended)
   - Set `USE_SUPABASE_AUTH=true` in environment
   - Configure Supabase project with Google OAuth provider
   - Update redirect URIs in Google Cloud Console

2. **Add Additional Providers**
   - GitHub, Microsoft, LinkedIn OAuth
   - Email/Password authentication
   - Magic link authentication

3. **Enhanced Security**
   - Implement rate limiting
   - Add CSRF protection
   - Enable 2FA support

## Status
✅ OAuth routes are properly configured
✅ Backend and frontend services are running
✅ Nginx is configured for routing
✅ Authentication flow is ready for end-to-end testing

The Google OAuth authentication system is now fully configured and ready for use.
