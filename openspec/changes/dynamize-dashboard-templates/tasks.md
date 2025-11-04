# Implementation Tasks

## 1. Add Template Data Structure
- [ ] 1.1 Open `/anwalts-frontend-new/pages/dashboard.vue`
- [ ] 1.2 Add `templates` ref after line 606:
  ```javascript
  const templates = ref([])
  ```
- [ ] 1.3 Add TypeScript interface (if using TypeScript):
  ```typescript
  interface Template {
    id: string
    name: string
    title?: string
    category: string
    version?: string
    status?: 'draft' | 'published'
    created_at: string
    updated_at?: string
  }
  ```

## 2. Add Date Formatting Helper
- [ ] 2.1 Add `formatDate()` function around line 648:
  ```javascript
  function formatDate(dateStr) {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return date.toLocaleDateString('de-DE', { 
      day: '2-digit', 
      month: 'short',
      year: 'numeric'
    })
  }
  ```

## 3. Add Template Fetching Function
- [ ] 3.1 Add `fetchTemplates()` function around line 660:
  ```javascript
  async function fetchTemplates() {
    try {
      const response = await fetch('/api/templates', {
        headers: getAuthHeader()
      })
      if (response.ok) {
        const data = await response.json()
        templates.value = data.templates || data || []
        console.log('✅ Loaded templates:', templates.value.length)
      } else {
        console.warn('Templates API returned non-OK status:', response.status)
        // Keep templates empty - will show static fallback
      }
    } catch (err) {
      console.error('Failed to load templates:', err)
      // Keep templates empty - will show static fallback
    }
  }
  ```

## 4. Call fetchTemplates on Mount
- [ ] 4.1 Add to `onMounted()` around line 684 (after `fetchSummary()`):
  ```javascript
  // Fetch templates
  await fetchTemplates()
  ```

## 5. Replace Static Templates with Dynamic Loop
- [ ] 5.1 Locate templates section (lines 206-291)
- [ ] 5.2 Replace entire template grid with:
  ```vue
  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
    <!-- Dynamic templates from API -->
    <template v-if="templates && templates.length > 0">
      <div v-for="template in templates.slice(0, 6)" 
           :key="template.id" 
           class="template-card">
        <div class="flex items-start justify-between">
          <div>
            <p class="font-medium">{{ template.title || template.name }}</p>
            <p class="text-xs text-gray-500 mt-1">
              Letztes Update: {{ formatDate(template.updated_at || template.created_at) }}
              <template v-if="template.version"> · Version {{ template.version }}</template>
              <template v-if="template.status === 'published'"> · Freigegeben</template>
            </p>
          </div>
          <span class="badge badge-primary" :title="template.category || 'Kategorie'">
            {{ template.category || 'Allgemein' }}
          </span>
        </div>
        <div class="mt-4 flex items-center gap-2">
          <button 
            class="btn btn-primary" 
            :data-template="template.id" 
            :aria-label="`${template.title || template.name}-Vorlage erstellen`">
            Erstellen
          </button>
          <button class="btn btn-secondary" @click="navigateTo(`/templates/${template.id}`)">
            Ansehen
          </button>
        </div>
      </div>
    </template>
    
    <!-- Fallback: Static templates if API fails or returns empty -->
    <template v-else>
      <!-- Keep existing 6 hardcoded template divs as fallback -->
      <div class="template-card">
        <div class="flex items-start justify-between">
          <div>
            <p class="font-medium">NDA – Standard (DE)</p>
            <p class="text-xs text-gray-500 mt-1">Letztes Update: 12. Aug 2025 · Freigegeben</p>
          </div>
          <span class="badge badge-primary">Vertrag</span>
        </div>
        <div class="mt-4 flex items-center gap-2">
          <button class="btn btn-primary" data-template="nda">Erstellen</button>
          <button class="btn btn-secondary">Ansehen</button>
        </div>
      </div>
      
      <!-- ... other 5 static templates ... -->
    </template>
  </div>
  ```

## 6. Add Loading State (Optional)
- [ ] 6.1 Add `isLoadingTemplates` ref:
  ```javascript
  const isLoadingTemplates = ref(false)
  ```
- [ ] 6.2 Update fetchTemplates to set loading state:
  ```javascript
  isLoadingTemplates.value = true
  // ... fetch logic ...
  isLoadingTemplates.value = false
  ```
- [ ] 6.3 Add skeleton loader to template section:
  ```vue
  <div v-if="isLoadingTemplates" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
    <div v-for="i in 6" :key="i" class="skeleton-item"></div>
  </div>
  ```

## 7. Testing - Local Development
- [ ] 7.1 Start dev mode: `cd /root/anwalts-frontend-new && npm run dev`
- [ ] 7.2 Open dashboard: `http://localhost:3000/dashboard`
- [ ] 7.3 Open browser console
- [ ] 7.4 Verify templates loaded: Check for "✅ Loaded templates: X" message
- [ ] 7.5 Verify dynamic templates displayed (not static hardcoded ones)
- [ ] 7.6 Verify dates show real dates (not "Aug 2025")
- [ ] 7.7 Verify template buttons still work (navigate to assistant)

## 8. Testing - API Response
- [ ] 8.1 Test with real `/api/templates` response:
  ```bash
  curl http://localhost:8000/api/templates -H "Authorization: Bearer YOUR_TOKEN"
  ```
- [ ] 8.2 Verify response structure matches expected format
- [ ] 8.3 Test with 0 templates → verify fallback static templates show
- [ ] 8.4 Test with 10+ templates → verify only first 6 show

## 9. Testing - Error Handling
- [ ] 9.1 Simulate API failure (kill backend) → verify fallback templates show
- [ ] 9.2 Simulate slow API (network throttling) → verify loading state
- [ ] 9.3 Simulate malformed response → verify fallback templates show
- [ ] 9.4 Verify no console errors in any failure scenario

## 10. Code Cleanup
- [ ] 10.1 Search for hardcoded template dates:
  ```bash
  grep -n "Letztes Update:" /root/anwalts-frontend-new/pages/dashboard.vue
  ```
- [ ] 10.2 Verify all hardcoded dates removed (except in fallback)
- [ ] 10.3 Remove console.log statements used for debugging
- [ ] 10.4 Run linter: `npm run lint` (if configured)

## 11. Deployment
- [ ] 11.1 Clear build cache:
  ```bash
  cd /root/anwalts-frontend-new
  rm -rf .nuxt .output node_modules/.vite
  ```
- [ ] 11.2 Build Docker image:
  ```bash
  cd /root
  docker-compose build --no-cache frontend
  ```
- [ ] 11.3 Deploy:
  ```bash
  docker rm -f anwalts_frontend
  docker run -d --name anwalts_frontend --network root_default \
    -p 3000:3000 -e BACKEND_BASE=http://backend:8000 \
    --restart unless-stopped root_frontend:latest
  ```
- [ ] 11.4 Wait for health check: `sleep 20 && docker ps | grep anwalts_frontend`
- [ ] 11.5 Verify dashboard loads: `curl -I http://localhost:3000/dashboard`

## 12. Production Verification
- [ ] 12.1 Load dashboard in browser: `http://localhost:3000/dashboard`
- [ ] 12.2 Verify templates show real data (not hardcoded Aug 2025 dates)
- [ ] 12.3 Verify template count matches database
- [ ] 12.4 Test template "Erstellen" buttons work
- [ ] 12.5 Test template "Ansehen" buttons work
- [ ] 12.6 Check browser console for errors (should be none)
- [ ] 12.7 Test as different users (admin vs regular user)

## 13. Monitoring
- [ ] 13.1 Monitor logs for template loading errors
- [ ] 13.2 Verify `/api/templates` response time < 200ms
- [ ] 13.3 Check for any dashboard load failures
- [ ] 13.4 Monitor for 24 hours post-deployment

## 14. Documentation
- [ ] 14.1 Update dashboard documentation
- [ ] 14.2 Add comment explaining template fetching logic
- [ ] 14.3 Document template data structure
- [ ] 14.4 Update deployment notes

## 15. Archive Change
- [ ] 15.1 After successful deployment:
  ```bash
  cd /root
  openspec archive dynamize-dashboard-templates --yes
  ```
- [ ] 15.2 Validate:
  ```bash
  openspec validate --strict
  ```

---

## Notes

- **Total estimated time**: 3-4 hours (including testing)
- **Risk level**: LOW - Fallback ensures dashboard always shows something
- **Dependencies**: `/api/templates` endpoint must exist and be accessible
- **Rollback plan**: Revert to previous Docker image (static templates)

## Quick Commands Reference

```bash
# Start dev mode for testing
cd /root/anwalts-frontend-new && npm run dev

# Test API endpoint
curl http://localhost:8000/api/templates -H "Authorization: Bearer TOKEN"

# Build and deploy
cd /root
docker-compose build --no-cache frontend
docker rm -f anwalts_frontend
docker run -d --name anwalts_frontend --network root_default \
  -p 3000:3000 -e BACKEND_BASE=http://backend:8000 \
  --restart unless-stopped root_frontend:latest

# Verify
docker ps | grep anwalts_frontend
curl -I http://localhost:3000/dashboard

# Archive
openspec archive dynamize-dashboard-templates --yes
```
