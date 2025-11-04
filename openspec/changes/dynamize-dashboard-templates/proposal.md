# Dynamize Dashboard Templates Section

## Change ID
`dynamize-dashboard-templates`

## Why

The dashboard templates section currently displays **hardcoded template data**:
- 6 templates with fake update dates ("12. Aug 2025", "30. Jul 2025", etc.)
- Static HTML repeated 6 times instead of using dynamic loops
- No connection to actual template database
- Cannot reflect real template changes, versions, or metadata

This creates several problems:
1. **Stale data** - Dates never update to reflect actual template changes
2. **Maintenance burden** - Adding/removing templates requires HTML editing
3. **Inconsistency** - Templates shown may not match what's actually available in `/api/templates`
4. **Scalability** - Cannot show user-specific favorites or recently used templates

Users expect the dashboard to show **real, current template data** from the system, not fake static content.

## What Changes

### Frontend Changes

1. **Add Template Fetching** (`/pages/dashboard.vue`):
   - Add `templates` ref to store template data
   - Create `fetchTemplates()` function to call `/api/templates`
   - Call `fetchTemplates()` in `onMounted()`
   - Handle loading/error states

2. **Replace Static HTML with Dynamic Loop** (lines 207-291):
   - Remove all 6 hardcoded template `<div>` blocks
   - Replace with single `v-for="template in templates.slice(0, 6)"`
   - Bind template data dynamically (title, date, version, category)
   - Keep fallback static templates if API fails

3. **Format Dates Dynamically**:
   - Add `formatDate()` helper function
   - Display real `updated_at` or `created_at` from API
   - Format as "DD. MMM YYYY" (e.g., "15. Nov 2025")

4. **Dynamic Metadata Display**:
   - Show real version numbers from API
   - Show real statuses ("Freigegeben" if published)
   - Show real categories from template data

### Backend Changes

**NONE** - The `/api/templates` endpoint already exists and returns template data. This is purely a frontend integration change.

## Impact

### Affected Files

**Frontend:**
- `/anwalts-frontend-new/pages/dashboard.vue` - Lines 207-291 (templates section)
  - Add `templates` ref
  - Add `fetchTemplates()` function
  - Add `formatDate()` helper
  - Replace static HTML with `v-for` loop

**Backend:**
- No changes needed (endpoint exists)

### User Experience Impact

- **Positive**: Templates show real, current data
- **Positive**: Template list updates automatically when templates change
- **Positive**: Users see accurate update dates and versions
- **Positive**: Can show more than 6 templates dynamically (future enhancement)
- **Neutral**: Visual appearance remains identical
- **Risk**: If API fails, dashboard shows fewer templates (mitigated by fallback static templates)

### Performance Impact

- One additional API call on dashboard load (`GET /api/templates`)
- Expected response time: <200ms
- Negligible impact (dashboard already makes multiple API calls)

## Alternatives Considered

### Alternative 1: Keep Static Templates (NOT CHOSEN)
- **Pros**: No API dependency, always shows something
- **Cons**: Data is fake and never updates
- **Reason for rejection**: Defeats purpose of showing "real" data

### Alternative 2: Fetch Templates on Every Page View (NOT CHOSEN)
- **Pros**: Always fresh data
- **Cons**: Unnecessary load for rarely-changing data
- **Reason for rejection**: Can add caching later if needed; over-optimization

### Alternative 3: Server-Side Render Templates (NOT CHOSEN)
- **Pros**: Faster initial page load
- **Cons**: Complicates SSR setup, not needed for dashboard
- **Reason for rejection**: Dashboard is behind auth, client-side fetch is fine

## Compatibility

- **No breaking changes**: Dashboard continues to work, just with real data
- **Backward compatible**: Fallback to static templates if API fails
- **Graceful degradation**: Loading states show skeletons, errors show fallback
- **No data migration**: No database changes needed

## Dependencies

- Requires `/api/templates` endpoint (already exists)
- Requires auth system to fetch templates per user (already works)

## Success Criteria

1. ✅ Templates displayed show real data from `/api/templates` endpoint
2. ✅ Template dates show actual update dates (not hardcoded "Aug 2025")
3. ✅ Template versions show real version numbers from database
4. ✅ Adding/removing templates in database reflects on dashboard
5. ✅ API failure shows fallback static templates (graceful degradation)
6. ✅ Loading state shows skeleton while fetching
7. ✅ Template "Erstellen" buttons continue to work (navigate to assistant)

## Testing Plan

1. **API Integration Testing**:
   - Verify `/api/templates` returns expected data structure
   - Test with 0 templates (empty state)
   - Test with 1-5 templates (show all)
   - Test with 10+ templates (show only 6)

2. **Date Formatting Testing**:
   - Verify German date format ("15. Nov 2025")
   - Test with various date formats from API
   - Test with missing dates (show fallback)

3. **Error Handling Testing**:
   - Simulate API failure → verify static templates show
   - Simulate slow API → verify loading skeleton shows
   - Simulate malformed API response → verify fallback

4. **User Testing**:
   - Load dashboard as regular user → see templates
   - Load dashboard as admin → see templates
   - Verify template buttons still work after dynamization

## Rollout Plan

1. **Phase 1**: Add template fetching and refs (no visual change yet)
2. **Phase 2**: Replace static HTML with dynamic loop
3. **Phase 3**: Test with real API data
4. **Phase 4**: Deploy to production
5. **Phase 5**: Monitor for API errors

## Notes

- This change aligns with existing `dynamize-dashboard-data` effort
- Templates section is one of the last hardcoded sections remaining
- Once complete, dashboard will be fully dynamic (except templates fallback)
- Future enhancement: User-specific template favorites, search, filtering
