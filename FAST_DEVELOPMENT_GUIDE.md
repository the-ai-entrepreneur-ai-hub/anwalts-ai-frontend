# ? Fast Development Guide - Nuxt Dev Mode

## ?? Goal
**Reduce development iteration from 6 minutes to < 1 second**

## ?? Quick Start

### Option 1: Full Dev Mode (Recommended)

```bash
# Terminal 1: Start backend services via Docker
cd /root
docker-compose up -d backend postgres redis mailhog

# Terminal 2: Start frontend in dev mode
cd /root/anwalts-frontend-new
npm run dev

# Open browser: http://localhost:3000
# Edit any file - changes appear INSTANTLY!
```

### Option 2: Specific Port

```bash
# If port 3000 is taken
cd /root/anwalts-frontend-new
PORT=3001 npm run dev

# Then access: http://localhost:3001
```

## ? Speed Comparison

| Task | Docker Production | Nuxt Dev Mode |
|------|-------------------|---------------|
| **CSS Change** | 5-6 minutes | < 1 second |
| **Component Edit** | 5-6 minutes | < 1 second |
| **API Route Change** | 3-4 minutes | 2-3 seconds |
| **Error Visibility** | Hidden in logs | Browser overlay |

## ??? What Happens in Dev Mode

### Hot Module Replacement (HMR)
- **CSS changes**: Instant injection (no page reload)
- **Vue components**: Fast reload with state preservation
- **API routes**: Auto-restart (2-3 seconds)
- **Type errors**: Show in browser overlay

### Development Features
? **Vue DevTools** - Inspect components, Pinia stores, router  
? **Nuxt DevTools** - Performance insights, component tree  
? **Source Maps** - Debug original TypeScript/Vue code  
? **Error Overlays** - See errors in browser (not buried in Docker logs)  
? **Auto-restart** - Detects config changes  

## ?? File Types & Reload Speed

| File Type | Reload Time | Notes |
|-----------|-------------|-------|
| `.css` | < 0.5s | HMR injection |
| `.vue` | < 1s | Component hot reload |
| `.ts` / `.js` | 1-2s | Fast recompile |
| `nuxt.config.ts` | 3-5s | Full server restart |
| `package.json` | Manual | Run `npm install` |

## ?? Configuration

### Backend Connection

The `.env` file is already configured for local dev:

```bash
# Frontend connects to Docker backend on localhost
BACKEND_BASE=http://localhost:8000
```

This works because:
- Backend container exposes `0.0.0.0:8000->8000`
- Frontend dev server can reach `localhost:8000`
- No Docker networking needed for frontend in dev mode

### Environment Variables

All env vars in `.env` are automatically loaded:
- `SUPABASE_URL` - Already configured
- `BACKEND_BASE` - Points to localhost:8000
- `GOOGLE_CLIENT_ID/SECRET` - OAuth credentials

## ?? Example Workflow: CSS Changes

### Before (Docker):
```bash
# 1. Edit main.css
vim /root/anwalts-frontend-new/assets/css/main.css

# 2. Clear cache
cd /root/anwalts-frontend-new
rm -rf .nuxt .output node_modules/.vite

# 3. Rebuild Docker
cd /root
docker-compose build --no-cache frontend  # 3-5 minutes

# 4. Restart containers
docker-compose up -d  # 1 minute

# 5. Verify changes
curl http://localhost:3000/settings

# TOTAL: ~6 minutes ?
```

### After (Dev Mode):
```bash
# 1. Edit main.css
vim /root/anwalts-frontend-new/assets/css/main.css

# 2. Save file
# Browser auto-refreshes with changes

# TOTAL: < 1 second ?
```

## ?? Debugging

### Browser DevTools
```javascript
// In browser console:
$nuxt           // Access Nuxt instance
$router         // Vue Router
$pinia          // Pinia store
```

### Vue DevTools
1. Install browser extension: [Vue DevTools](https://devtools.vuejs.org/)
2. Open DevTools ? Vue tab
3. Inspect components, state, events

### Nuxt DevTools
1. Already enabled in `nuxt.config.ts`
2. Look for floating icon in bottom-right corner
3. Click to open performance insights

## ?? Common Issues

### Port Already in Use
```bash
# Check what's using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or use different port
PORT=3001 npm run dev
```

### Backend Connection Fails
```bash
# Verify backend is running
docker ps --filter "name=anwalts_backend"

# Check backend health
curl http://localhost:8000/health

# Verify .env has correct BACKEND_BASE
cat /root/anwalts-frontend-new/.env | grep BACKEND_BASE
# Should show: BACKEND_BASE=http://localhost:8000
```

### Changes Not Appearing
```bash
# Hard refresh browser
Ctrl + Shift + R  (Linux/Windows)
Cmd + Shift + R   (Mac)

# Clear Nuxt cache
cd /root/anwalts-frontend-new
rm -rf .nuxt

# Restart dev server
npm run dev
```

### TypeScript Errors
```bash
# Regenerate types
npm run postinstall

# Check for errors
npx nuxi typecheck
```

## ?? Performance Tips

### Faster Startup
```bash
# Skip type checking on startup (faster)
NUXT_TYPECHECK=false npm run dev
```

### Reduce Memory Usage
```bash
# Limit Node memory (if running low)
NODE_OPTIONS="--max-old-space-size=4096" npm run dev
```

### Disable DevTools (if lagging)
```javascript
// nuxt.config.ts
export default defineNuxtConfig({
  devtools: { enabled: false },  // Disable if causing lag
})
```

## ?? When to Use Each Mode

### Use Dev Mode For:
? CSS/styling changes  
? Component development  
? Page layout adjustments  
? API route development  
? Debugging issues  
? Testing new features  

### Use Docker Build For:
? Final production testing  
? Deployment preparation  
? Docker-specific issues  
? CI/CD pipeline  
? Full integration testing  

## ?? Switching Between Modes

### From Docker ? Dev Mode
```bash
# 1. Stop frontend container only
docker-compose stop frontend

# 2. Start dev mode
cd /root/anwalts-frontend-new
npm run dev
```

### From Dev Mode ? Docker
```bash
# 1. Stop dev server (Ctrl+C)

# 2. Rebuild and start Docker
cd /root
docker-compose build frontend
docker-compose up -d frontend
```

## ?? Quick Reference Commands

```bash
# Start dev mode
npm run dev

# Build production (for Docker)
npm run build

# Preview production build locally
npm run preview

# Run tests
npm run test

# Type checking
npx nuxi typecheck

# Analyze bundle size
npx nuxi analyze
```

## ?? Summary

**Before**: Edit ? Clear cache ? Rebuild Docker ? Wait 6 minutes ? Test  
**After**: Edit ? See changes instantly ? Done!

**Development time savings**: ~95% faster iteration ??

## ?? Useful Links

- [Nuxt Documentation](https://nuxt.com/docs)
- [Vue DevTools](https://devtools.vuejs.org/)
- [Vite Documentation](https://vite.dev/)
- [Hot Module Replacement (HMR)](https://vite.dev/guide/features.html#hot-module-replacement)
