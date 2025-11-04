# Technical Design: Settings Analytics UI Rebuild

## Architecture Decisions

### 1. CSS Approach: Scoped CSS Over Tailwind Utilities

**Decision:** Use Vue scoped CSS exclusively for Settings Analytics tab.

**Rationale:**
- Previous approach mixed Tailwind utilities with custom CSS causing conflicts
- Removing Tailwind utilities from main.css broke all utility-based layouts
- Scoped CSS provides isolation and prevents global conflicts
- Easier to debug: all styles in one place
- No dependency on Tailwind configuration

**Implementation:**
```vue
<style scoped>
.settings-analytics-container {
  /* All styles here */
}
</style>
```

### 2. Spacing Strategy: Margins Over Gap

**Decision:** Use `margin-bottom` for section spacing, NOT flexbox `gap`.

**Rationale:**
- Flexbox gap has compatibility issues in older browsers
- Gap property doesn't work consistently across all rendering engines
- Margin-bottom is universally supported since IE6
- Explicit margins easier to debug in DevTools
- No surprises with collapsing margins (controlled with `:last-child`)

**Implementation:**
```css
.section-kpi {
  margin-bottom: 40px;
}

.section-kpi:last-child {
  margin-bottom: 0; /* Prevent extra space at bottom */
}
```

### 3. Layout: CSS Grid Over Flexbox

**Decision:** Use CSS Grid for card layouts.

**Rationale:**
- Grid better suited for 2D layouts (rows and columns)
- More predictable spacing with `gap` in grid vs flexbox
- Easier responsive breakpoints with `grid-template-columns`
- Better browser support for grid gap than flexbox gap
- Cleaner code with fewer wrapper divs

**Implementation:**
```css
.card-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

@media (min-width: 768px) {
  .card-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .card-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

### 4. Component Structure: Semantic HTML

**Decision:** Use semantic HTML5 elements with descriptive class names.

**Rationale:**
- Better accessibility for screen readers
- Clearer code structure and maintainability
- SEO benefits (though not critical for authenticated pages)
- Easier testing with semantic selectors

**Implementation:**
```html
<section class="settings-analytics-container">
  <div class="section-kpi">
    <div class="card-grid-4">
      <article class="card card-kpi">...</article>
    </div>
  </div>
  
  <div class="section-meta">
    <div class="card-grid-3">
      <article class="card card-meta">...</article>
    </div>
  </div>
  
  <div class="section-health">
    <h2 class="section-title">Systemstatus</h2>
    <div class="card card-full">
      <div class="health-grid">
        <div class="health-item">...</div>
      </div>
    </div>
  </div>
  
  <div class="section-charts">
    <div class="card-grid-2">
      <article class="card card-chart">...</article>
    </div>
  </div>
</section>
```

### 5. Responsive Approach: Mobile-First

**Decision:** Design for mobile first, progressively enhance for desktop.

**Rationale:**
- Majority of traffic from mobile devices
- Easier to add complexity than remove it
- Forces focus on essential content
- Better performance on low-end devices

**Breakpoints:**
```css
/* Base: Mobile (320px+) */
.card-grid { grid-template-columns: 1fr; }

/* Tablet (768px+) */
@media (min-width: 768px) {
  .card-grid-2 { grid-template-columns: repeat(2, 1fr); }
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
  .card-grid-3 { grid-template-columns: repeat(3, 1fr); }
  .card-grid-4 { grid-template-columns: repeat(4, 1fr); }
}
```

### 6. Color System: CSS Custom Properties

**Decision:** Define colors as CSS variables for consistency.

**Rationale:**
- Easy to maintain and update
- Single source of truth for colors
- Supports future dark mode implementation
- Better performance than inline styles

**Implementation:**
```css
:root {
  --color-text-primary: #111827;
  --color-text-secondary: #6b7280;
  --color-bg-card: #ffffff;
  --color-border: #e5e7eb;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --spacing-section: 40px;
  --spacing-card: 24px;
  --radius-card: 12px;
}
```

### 7. Loading States: Skeleton Screens

**Decision:** Show skeleton loaders maintaining exact layout dimensions.

**Rationale:**
- Reduces perceived load time
- Prevents layout shift (better CLS score)
- Shows user something is happening
- Maintains spacing even before data loads

**Implementation:**
```vue
<div v-if="loading" class="skeleton-kpi">
  <div class="skeleton-card"></div>
  <div class="skeleton-card"></div>
  <div class="skeleton-card"></div>
  <div class="skeleton-card"></div>
</div>

<div v-else class="card-grid-4">
  <article v-for="kpi in kpis" ...>
</div>
```

```css
.skeleton-card {
  height: 160px;
  background: linear-gradient(
    90deg,
    #f3f4f6 25%,
    #e5e7eb 50%,
    #f3f4f6 75%
  );
  background-size: 200% 100%;
  animation: loading 1.5s ease-in-out infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

### 8. Error Handling: Graceful Degradation

**Decision:** Show partial data if some endpoints fail, maintain layout.

**Rationale:**
- Better user experience than complete failure
- Users can still see available information
- Layout doesn't break if one section fails
- Clear error messages for failed sections

**Implementation:**
```vue
<div class="section-kpi">
  <div v-if="errors.kpi" class="error-message">
    KPI-Daten konnten nicht geladen werden.
    <button @click="retryKpi">Erneut versuchen</button>
  </div>
  <div v-else class="card-grid-4">
    <!-- Cards -->
  </div>
</div>

<!-- Other sections continue to render -->
```

### 9. Cache Busting: Versioned Assets

**Decision:** Add version parameter to CSS file URLs.

**Rationale:**
- Forces browsers to load new CSS
- Prevents users seeing old cached styles
- No need for manual cache clearing instructions
- Standard web practice for cache control

**Implementation:**
```javascript
// nuxt.config.ts
export default defineNuxtConfig({
  app: {
    head: {
      link: [
        {
          rel: 'stylesheet',
          href: `/settings.css?v=${Date.now()}`
        }
      ]
    }
  },
  nitro: {
    compressPublicAssets: true,
    routeRules: {
      '/_nuxt/**': {
        headers: {
          'Cache-Control': 'public, max-age=31536000, immutable'
        }
      },
      '/settings': {
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate'
        }
      }
    }
  }
})
```

### 10. Typography: System Font Stack

**Decision:** Use system font stack for optimal performance.

**Rationale:**
- No web font download required (faster)
- Native look and feel on each platform
- Better rendering performance
- Accessibility (users' preferred fonts)

**Implementation:**
```css
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
               Roboto, Oxygen, Ubuntu, Cantarell, 
               'Helvetica Neue', sans-serif;
}
```

## Data Flow

### API Integration

```
Component Mount
    ↓
Call loadOverview()
    ↓
Fetch /api/settings/overview
    ↓
Parse Response
    ↓
Update Reactive State
    ├─ kpis[]
    ├─ overviewMeta{}
    ├─ systemHealth[]
    ├─ userGrowthSeries[]
    └─ apiUsageSeries[]
    ↓
Trigger Re-render
    ↓
Display Cards
```

### State Management

```javascript
// Reactive state
const kpis = ref([
  { label: 'Aktive Benutzer', value: '13', change: -100, iconPath: '...' },
  { label: 'Dokumente', value: '4', change: 0, iconPath: '...' },
  { label: 'Neue Fälle', value: '0', change: 0, iconPath: '...' },
  { label: 'API-Aufrufe', value: '3,280', change: 45.84, iconPath: '...' }
])

const overviewMeta = ref({
  templates_total: 6,
  webhooks_total: 0,
  api: {
    success_rate: 99.7,
    avg_latency_ms: 585
  }
})

const systemHealth = ref([
  { name: 'PostgreSQL', status: 'Störung', uptime: 0, latency_ms: null },
  { name: 'Redis Cache', status: 'Störung', uptime: 0, latency_ms: null },
  { name: 'KI-Service', status: 'Betriebsbereit', uptime: 100, latency_ms: 1027 },
  { name: 'Webserver', status: 'Störung', uptime: 0, latency_ms: null }
])
```

## Performance Targets

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Page Load Time | < 2s | TBD | 🟡 |
| First Contentful Paint | < 1s | TBD | 🟡 |
| Largest Contentful Paint | < 2.5s | TBD | 🟡 |
| Cumulative Layout Shift | < 0.1 | TBD | 🟡 |
| First Input Delay | < 100ms | TBD | 🟡 |
| CSS Bundle Size | < 10KB | TBD | 🟡 |
| Total Page Size | < 500KB | TBD | 🟡 |

## Browser Support Matrix

| Browser | Min Version | Status | Notes |
|---------|-------------|--------|-------|
| Chrome | 90+ | ✅ Full | Primary development browser |
| Firefox | 88+ | ✅ Full | CSS Grid fully supported |
| Safari | 14+ | ✅ Full | Flexbox gap supported from 14.1 |
| Edge | 90+ | ✅ Full | Chromium-based, same as Chrome |
| Mobile Safari | 14+ | ✅ Full | iOS 14+ required |
| Chrome Android | 90+ | ✅ Full | Same as desktop Chrome |

**Unsupported:** IE11 (deprecated, < 0.5% market share)

## Security Considerations

1. **No sensitive data in CSS** - All colors and dimensions safe to cache
2. **CSP compliant** - No inline styles that violate CSP
3. **XSS prevention** - All data sanitized before rendering
4. **CSRF protection** - Read-only page, no state-changing operations

## Accessibility Requirements

1. **Keyboard navigation** - All interactive elements focusable with Tab
2. **Screen reader support** - Proper ARIA labels and semantic HTML
3. **Color contrast** - WCAG AA minimum (4.5:1 for text)
4. **Focus indicators** - Visible focus rings on all interactive elements
5. **Zoom support** - Layout works at 200% zoom
6. **Motion preferences** - Respect `prefers-reduced-motion`

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Testing Strategy

### Unit Tests
- Test data transformation functions
- Test computed properties
- Test error handling logic

### Integration Tests
- Test API data loading
- Test state updates
- Test error recovery

### Visual Regression Tests
- Screenshot comparison at all breakpoints
- Test in all supported browsers
- Verify spacing is pixel-perfect

### Accessibility Tests
- Automated Lighthouse audits
- Manual screen reader testing
- Keyboard navigation testing

### Performance Tests
- Lighthouse performance audits
- Network throttling tests
- Memory leak detection

## Deployment Strategy

### Build Process
```bash
# 1. Install dependencies
npm ci

# 2. Build production
npm run build

# 3. Verify build
ls -lh .output/public/_nuxt/settings.*.css

# 4. Deploy to container
docker cp .output anwalts_frontend:/app/

# 5. Restart container
docker restart anwalts_frontend

# 6. Verify health
docker ps | grep anwalts_frontend
```

### Rollback Procedure
```bash
# 1. Get backup filename
BACKUP=$(ls -t /root/settings.vue.backup.* | head -1)

# 2. Restore backup
cp $BACKUP /root/anwalts-frontend-new/pages/settings.vue

# 3. Rebuild
cd /root/anwalts-frontend-new && npm run build

# 4. Redeploy
docker restart anwalts_frontend
```

### Monitoring

**Metrics to Track:**
- Page load times (RUM data)
- Error rates from browser console
- User complaints/support tickets
- Google Analytics engagement metrics

**Alerts:**
- Page load time > 3 seconds
- Error rate > 1%
- Increase in bounce rate > 10%

## Future Enhancements

1. **Dark mode support** - Use CSS variables for easy theming
2. **Real-time updates** - WebSocket connection for live metrics
3. **Customizable dashboards** - User-configurable card layout
4. **Export functionality** - Download metrics as PDF/CSV
5. **Historical data** - Time-series charts for trends
6. **Alerts integration** - Show system alerts inline
7. **Mobile app** - Native mobile version
8. **Internationalization** - Multi-language support
