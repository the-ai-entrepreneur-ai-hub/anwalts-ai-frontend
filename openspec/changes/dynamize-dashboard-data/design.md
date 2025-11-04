# Technical Design: Dynamize Dashboard Data

## Context

The dashboard currently serves as a demo/placeholder with entirely hard-coded values. This design doc outlines how to transform it into a functional, personalized dashboard that displays real user data.

**Stakeholders:**
- End users (lawyers) who need accurate case/document/deadline information
- Angela (admin) who reported issues with hard-coded values in other features
- Development team maintaining the dashboard code

**Constraints:**
- Must work with existing Nuxt 3 + TypeScript frontend architecture
- Must integrate with existing Supabase/PostgreSQL database
- Must use existing authentication system (`usePortalUser()` composable)
- Cannot break existing UI/UX - only data source changes
- Must perform well (<2s load time) even with database queries

**Current Architecture:**
- Frontend: Nuxt 3 (Vue 3 + TypeScript) with Pinia stores
- Backend: Nuxt server routes (Nitro) acting as API layer
- Database: PostgreSQL (accessed via `database.py` Python functions and asyncpg)
- Auth: Mixed Stack Auth + custom JWT tokens, resolved via `usePortalUser()`

## Goals / Non-Goals

### Goals
1. **Remove ALL hard-coded values** - No more fake "42 cases" or "Klageentwurf Schmidt"
2. **Personalize per user** - Dashboard shows data specific to logged-in user
3. **Real-time data** - Dates/times calculated relative to current moment
4. **Graceful empty states** - New users see helpful empty states, not broken UI
5. **Maintainable code** - Clear data flow from DB ? API ? Store ? Component

### Non-Goals
1. **Not adding new dashboard features** - No analytics, charts, or insights (yet)
2. **Not creating admin analytics dashboard** - This is for individual users, not system-wide metrics
3. **Not optimizing for thousands of records** - Limiting to recent 3-5 items per section is sufficient
4. **Not adding real-time updates** - Fetching on page load is sufficient; no WebSocket needed
5. **Not backwards-compatible with old data format** - Hard-coded data is discarded, not migrated

## Decisions

### Decision 1: Expand Existing API vs. Create Multiple Endpoints

**Options:**
- **A)** Single endpoint `/api/dashboard/summary` returns ALL dashboard data (stats, docs, deadlines, activity)
- **B)** Multiple endpoints: `/api/dashboard/stats`, `/api/dashboard/documents`, `/api/dashboard/deadlines`, etc.

**Choice: Option A (Single comprehensive endpoint)**

**Rationale:**
- Dashboard components load together, no need for separate requests
- Reduces HTTP overhead (1 request vs. 5 requests)
- Simpler state management (1 fetch call in store)
- Easier to ensure consistency (all data from same transaction/moment)
- Can always split later if performance becomes an issue

**Implementation:**
- `/api/dashboard/summary.get.ts` returns:
  ```typescript
  {
    stats: { newCases, documents, emails, nextDeadline },
    recentDocuments: [...],
    upcomingDeadlines: [...],
    recentActivity: [...],
    continueSuggestion: { ... },
    user: { name, email }
  }
  ```

### Decision 2: Database Layer Architecture

**Options:**
- **A)** Query database directly from Nuxt server routes using `useSupabaseServer()`
- **B)** Call Python backend (`database.py`) via HTTP from Nuxt server routes
- **C)** Hybrid: Use Supabase for simple queries, Python backend for complex logic

**Choice: Option C (Hybrid approach)**

**Rationale:**
- Supabase queries are fast and simple for basic counts/lists
- Python backend already has complex logic (email encryption, etc.)
- Reduces latency for dashboard-specific queries (no HTTP hop to Python)
- Maintains consistency with existing patterns (some endpoints use Supabase, some use Python)

**Implementation:**
- Use `useSupabaseServer(event).from('documents').select()` for documents list
- Use `useSupabaseServer(event).from('cases').select()` for case counts (if table exists)
- Call Python backend only if complex business logic needed (e.g., email processing)

### Decision 3: Database Schema Strategy

**Options:**
- **A)** Create new tables (`cases`, `deadlines`, `activities`) even if data doesn't exist yet
- **B)** Only create tables if we have actual data to populate them
- **C)** Use existing `documents` table for everything, add columns as needed

**Choice: Option A (Create tables proactively)**

**Rationale:**
- Defines clear schema for future data entry
- Allows empty state testing (no data, but table exists)
- Avoids "table doesn't exist" errors in production
- Migrations can be run safely before feature is fully populated
- Better than checking "if table exists" in every query

**Implementation:**
- Migration file: `migrations/create_dashboard_tables.sql`
- Creates: `cases`, `deadlines`, `activities` tables with proper indexes
- Add columns to `documents`: `user_id`, `progress` (int 0-100), `status` (enum)

### Decision 4: Handling Missing Data

**Options:**
- **A)** Return errors if database is empty (404 or 500)
- **B)** Return empty arrays/zeros and let frontend show empty states
- **C)** Return placeholder data (like current hard-coded values)

**Choice: Option B (Empty arrays/zeros)**

**Rationale:**
- Dashboard should never "break" - always render something
- Empty states already exist in UI (e.g., "Noch keine Dokumente")
- Zeros are semantically correct (user has 0 cases)
- Encourages users to add data (call-to-action buttons in empty states)

**Implementation:**
```typescript
const stats = {
  newCases: rows.length || 0,  // ? Return 0, not null or error
  documents: docs.length || 0,
  emails: emails.length || 0,
  nextDeadline: deadline?.due_date || null  // ? null is OK for optional field
}
```

### Decision 5: Date/Time Handling

**Options:**
- **A)** Backend returns dates as ISO strings, frontend does all formatting
- **B)** Backend returns pre-formatted strings ("vor 2 Stunden")
- **C)** Backend returns both: ISO timestamp + human-readable label

**Choice: Option A (Backend returns ISO, frontend formats)**

**Rationale:**
- Cleaner separation of concerns (backend = data, frontend = presentation)
- Supports internationalization (frontend can format in user's locale)
- Avoids timezone issues (frontend uses browser timezone)
- Easier testing (ISO strings are deterministic)

**Implementation:**
- Backend: `nextDeadline: deadline.due_date.isoformat()` (Python)
- Frontend: Use `date-fns` or native `Intl.RelativeTimeFormat` for "in 2 days"

### Decision 6: Templates Section Strategy

**Options:**
- **A)** Make templates user-specific (show "my templates")
- **B)** Keep templates organization-wide (current approach)
- **C)** Show templates but mark user's favorites

**Choice: Option B (Keep organization-wide for now)**

**Rationale:**
- Templates (NDA, contracts, pleadings) are typically shared resources
- No user feedback requesting personalized templates
- Reduces scope of this proposal (already large)
- Can add "favorite templates" later as separate feature

**Implementation:**
- Templates section remains mostly static (or fetched from `/api/templates`)
- Focus dynamization effort on stats, docs, deadlines, activity (user-specific data)

### Decision 7: Performance Optimization

**Options:**
- **A)** No optimization initially, add caching later if needed
- **B)** Implement Redis caching from the start
- **C)** Use database materialized views for dashboard stats

**Choice: Option A (No premature optimization)**

**Rationale:**
- Dashboard queries are simple (no joins, basic filters, LIMIT 3)
- PostgreSQL can handle these queries in <50ms with proper indexes
- Caching adds complexity and potential staleness issues
- Measure first, optimize later (YAGNI principle)

**Implementation:**
- Add indexes: `CREATE INDEX idx_documents_user_id ON documents(user_id)`
- Use `LIMIT` clauses to restrict result sets (3-5 items per section)
- If load time >2s in production, revisit caching strategy

### Decision 8: Error Handling Strategy

**Options:**
- **A)** Fail entire dashboard if any query fails (show error page)
- **B)** Gracefully degrade: Show sections that work, hide sections that fail
- **C)** Return partial data with warnings array

**Choice: Option C (Partial data + warnings)**

**Rationale:**
- Dashboard should always render something useful
- Users shouldn't see blank screen because deadlines query failed
- Warnings inform user of issues without blocking UX
- Aligns with existing `/api/dashboard/summary` pattern (already has `warnings` field)

**Implementation:**
```typescript
try {
  const docs = await fetchDocuments(userId)
} catch (err) {
  warnings.push('Dokumente konnten nicht geladen werden')
  docs = []  // ? Return empty array, not error
}
```

## Data Flow Architecture

```
???????????????????????????????????????????????????????????????????
? User Loads Dashboard                                            ?
???????????????????????????????????????????????????????????????????
                                    ?
                                    ?
???????????????????????????????????????????????????????????????????
? Frontend: /pages/dashboard.vue                                  ?
? - onMounted() triggers data fetch                               ?
? - Shows loading skeletons                                       ?
???????????????????????????????????????????????????????????????????
                                    ?
                                    ?
???????????????????????????????????????????????????????????????????
? Store: dashboardStore.fetchSummary()                            ?
? - Calls $fetch('/api/dashboard/summary')                       ?
? - Stores result in reactive refs                                ?
???????????????????????????????????????????????????????????????????
                                    ?
                                    ?
???????????????????????????????????????????????????????????????????
? API: /server/api/dashboard/summary.get.ts                       ?
? 1. Extract user from session (Supabase/JWT)                     ?
? 2. Query database for user-specific data                        ?
? 3. Aggregate results into response object                       ?
? 4. Return JSON to frontend                                      ?
???????????????????????????????????????????????????????????????????
                                    ?
                                    ?
???????????????????????????????????????????????????????????????????
? Database: PostgreSQL                                            ?
? - Query 1: SELECT COUNT(*) FROM cases WHERE user_id = ?         ?
? - Query 2: SELECT * FROM documents WHERE user_id = ? LIMIT 3    ?
? - Query 3: SELECT * FROM deadlines WHERE user_id = ? LIMIT 3    ?
? - Query 4: SELECT * FROM activities WHERE user_id = ? LIMIT 3   ?
? - Query 5: SELECT * FROM users WHERE id = ? (for name)          ?
???????????????????????????????????????????????????????????????????
```

## Database Schema Design

### New Table: `cases`
```sql
CREATE TABLE IF NOT EXISTS cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    case_number VARCHAR(100),
    status VARCHAR(50) DEFAULT 'open',  -- open, pending, closed
    client_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_cases_user_id ON cases(user_id);
CREATE INDEX idx_cases_created_at ON cases(created_at DESC);
```

### New Table: `deadlines`
```sql
CREATE TABLE IF NOT EXISTS deadlines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    due_date TIMESTAMP NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',  -- low, medium, high, urgent
    related_case_id UUID REFERENCES cases(id) ON DELETE SET NULL,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_deadlines_user_id ON deadlines(user_id);
CREATE INDEX idx_deadlines_due_date ON deadlines(due_date);
CREATE INDEX idx_deadlines_completed ON deadlines(completed);
```

### New Table: `activities`
```sql
CREATE TABLE IF NOT EXISTS activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL,  -- email, phone, upload, meeting
    title VARCHAR(500) NOT NULL,
    description TEXT,
    related_entity_type VARCHAR(50),  -- case, document, etc.
    related_entity_id UUID,
    status VARCHAR(50),  -- pending, completed, etc.
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_activities_user_id ON activities(user_id);
CREATE INDEX idx_activities_created_at ON activities(created_at DESC);
CREATE INDEX idx_activities_type ON activities(activity_type);
```

### Modified Table: `documents` (add columns)
```sql
ALTER TABLE documents ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'draft';  -- draft, in_progress, review, final
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
```

## API Response Format

```typescript
// Response from /api/dashboard/summary
{
  stats: {
    newCases: 5,           // Count of cases created in last 30 days
    documents: 23,         // Total document count for user
    emails: 142,           // Total email count for user
    nextDeadline: "2025-11-05T14:00:00Z"  // ISO timestamp of nearest deadline
  },
  recentDocuments: [
    {
      id: "abc-123",
      title: "Klageentwurf Schmidt",
      updated_at: "2025-11-02T10:30:00Z",
      status: "in_progress",
      progress: 80,
      details: "Zuletzt ge?ndert von M. Weber ? Version 12"
    }
    // ... up to 3 documents
  ],
  upcomingDeadlines: [
    {
      id: "def-456",
      title: "Beschwerdebegr?ndung",
      description: "OLG Stuttgart",
      due_date: "2025-11-02T23:59:59Z",
      priority: "urgent"
    }
    // ... up to 3 deadlines
  ],
  recentActivity: [
    {
      id: "ghi-789",
      type: "email",
      title: "Angebot Vergleich ? Glaser GmbH",
      client: "Schmidt",
      status: "review",
      created_at: "2025-11-02T08:15:00Z"
    }
    // ... up to 3 activities
  ],
  continueSuggestion: {
    id: "abc-123",
    title: "Klageentwurf Schmidt",
    progress: 80,
    deadline: "2025-11-05T23:59:59Z"
  } || null,
  user: {
    name: "Angela Generalao",
    email: "angelageneralao.1997@gmail.com"
  },
  warnings: []  // Array of warning messages if any queries failed
}
```

## Frontend Component Structure

```vue
<template>
  <div v-if="isLoading">
    <!-- Loading skeletons (already exist) -->
  </div>
  <div v-else-if="error">
    <!-- Error state -->
  </div>
  <div v-else>
    <h2>Willkommen zur?ck, {{ userName }}</h2>
    
    <!-- Stats cards -->
    <StatsCard label="Neue F?lle" :value="stats.newCases" />
    
    <!-- Documents -->
    <div v-for="doc in recentDocuments" :key="doc.id">
      {{ doc.title }} - {{ formatRelativeTime(doc.updated_at) }}
    </div>
    
    <!-- Deadlines -->
    <div v-for="deadline in upcomingDeadlines" :key="deadline.id">
      {{ deadline.title }} - {{ getRelativeDateLabel(deadline.due_date) }}
    </div>
  </div>
</template>

<script setup>
const dashboardStore = useDashboardStore()
const { user } = usePortalUser()

const stats = computed(() => dashboardStore.stats)
const recentDocuments = computed(() => dashboardStore.documents)
const upcomingDeadlines = computed(() => dashboardStore.deadlines)
const userName = computed(() => user.value?.name || 'Willkommen')

onMounted(async () => {
  await dashboardStore.fetchSummary()
})
</script>
```

## Risks / Trade-offs

### Risk 1: Database Query Performance
- **Risk**: Multiple queries per dashboard load could be slow
- **Mitigation**: Add database indexes, use LIMIT clauses, measure performance
- **Acceptable**: <2s total load time is fine for dashboard

### Risk 2: Empty Dashboard for New Users
- **Risk**: New users see all zeros, might think system is broken
- **Mitigation**: Excellent empty states with clear CTAs ("Create your first document")
- **Acceptable**: Empty state is honest and encourages engagement

### Risk 3: Data Inconsistency During Migration
- **Risk**: Some users have data in old format, some in new format
- **Mitigation**: This is not a migration - we're simply switching from fake to real data
- **Acceptable**: No old data to migrate; hard-coded values are discarded

### Risk 4: Timezone Issues
- **Risk**: Deadlines shown in wrong timezone (server vs. browser)
- **Mitigation**: Store deadlines in UTC, format in browser's local timezone
- **Acceptable**: Standard best practice, well-supported by JavaScript Date APIs

### Risk 5: Breaking Changes During Refactoring
- **Risk**: Accidentally changing UI/UX while refactoring data layer
- **Mitigation**: Keep all CSS/HTML structure identical, only change data sources
- **Acceptable**: Can be verified with visual regression testing or manual QA

## Migration Plan

### Phase 1: Database Setup (No User Impact)
1. Run migrations to create `cases`, `deadlines`, `activities` tables
2. Add columns to `documents` table
3. Verify migrations with `psql` queries

### Phase 2: Backend API Development (No User Impact)
1. Implement database query methods in `database.py`
2. Update `/api/dashboard/summary.get.ts` endpoint
3. Test with Postman/curl

### Phase 3: Frontend Integration (Requires Deployment)
1. Update dashboard store to fetch from API
2. Refactor dashboard component to use store data
3. Test locally with real backend

### Phase 4: Deployment
1. Deploy backend changes (database migrations + API updates)
2. Deploy frontend changes (rebuild Docker image)
3. Test in production with Angela's account

### Phase 5: Monitoring
1. Check logs for errors in first 24 hours
2. Monitor dashboard load times
3. Collect user feedback

## Open Questions

1. **Q**: Should we show system-wide stats to admins (e.g., total users, total documents)?
   - **A**: No, not in this proposal. Admin analytics dashboard is separate feature.

2. **Q**: Should we implement pagination for documents/deadlines (if user has 100+)?
   - **A**: Not yet. Limiting to 3 items is sufficient for dashboard overview. Full lists belong on dedicated pages.

3. **Q**: Should we cache dashboard data in Redis?
   - **A**: Not initially. Add caching only if performance testing shows it's needed.

4. **Q**: Should we add real-time updates (WebSocket) so dashboard auto-refreshes?
   - **A**: No. Fetching on page load is sufficient for V1. Consider for future enhancement.

5. **Q**: Should we support multiple languages for date formatting ("2 days" vs. "2 Tage")?
   - **A**: Out of scope for this proposal. Dashboard is currently German-only. i18n is separate feature.

## Success Metrics

- [ ] Dashboard shows different data for different logged-in users
- [ ] No hard-coded numbers remain in source code
- [ ] Dashboard load time <2 seconds
- [ ] Empty states render correctly for users with no data
- [ ] Dates are relative to current date (not hard-coded to 2025-08-21)
- [ ] No errors in browser console or server logs
- [ ] User feedback: "Dashboard is useful now" (vs. "Dashboard shows fake data")
