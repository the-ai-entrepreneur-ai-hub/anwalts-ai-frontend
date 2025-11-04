# Email Interface Redesign - Technical Design

## Context

The current email interface suffers from multiple UX issues:
- Duplicate navigation bars causing confusion
- Non-standard left sidebar navigation (not Gmail-like)
- Oversized modal buttons taking up too much space
- Poor screen real estate utilization

**Stakeholders**: Legal professionals who expect professional, familiar email interfaces

**Constraints**:
- Must maintain all existing email functionality
- Should feel familiar to Gmail/Outlook users
- Must be responsive across devices
- Should integrate cleanly with existing Nuxt/Vue architecture

## Goals / Non-Goals

### Goals
- Create a Gmail-inspired horizontal top navigation
- Eliminate navigation duplication
- Maximize email content viewing area
- Improve professional appearance
- Maintain all existing email features (folders, labels, search, compose, etc.)
- Ensure smooth, intuitive user experience

### Non-Goals
- Adding new email functionality (this is purely UI/UX redesign)
- Backend API changes
- Email provider integration changes
- Changing AI summary or attachment features

## Decisions

### Decision 1: Top Horizontal Navigation Pattern

**What**: Replace left sidebar with Gmail-style top horizontal navigation

**Why**:
- Industry standard (Gmail, Outlook, Apple Mail all use variations)
- Maximizes vertical space for email list
- Reduces navigation duplication
- Familiar to users

**Alternatives Considered**:
1. **Keep left sidebar, remove PortalShell** - Still non-standard, wastes horizontal space
2. **Hybrid approach with collapsible sidebar** - Adds complexity, still not Gmail-like
3. **Selected: Top horizontal nav** - Best alignment with user expectations and modern patterns

**Implementation**:
```vue
<!-- New structure -->
<div class="email-app-container">
  <!-- Top App Bar -->
  <header class="email-top-bar">
    <div class="email-logo">📧 E-Mail</div>
    <div class="email-search">...</div>
    <button class="compose-button-primary">+ Verfassen</button>
  </header>
  
  <!-- Horizontal Navigation -->
  <nav class="email-nav-tabs">
    <button v-for="folder in folders" :class="tab-item">
      <Icon /> {{ folder.label }} <Badge>{{ folder.count }}</Badge>
    </button>
    <!-- Labels as dropdown or filter chips -->
  </nav>
  
  <!-- Email Content Area -->
  <main class="email-content-area">
    <!-- Email list, controls, etc. -->
  </main>
</div>
```

### Decision 2: Remove PortalShell Wrapper

**What**: Create email-specific layout without PortalShell navigation

**Why**:
- Eliminates duplicate navigation
- Gives email section full control over layout
- Allows for email-optimized header design

**Alternatives Considered**:
1. **Conditionally hide PortalShell nav** - Hacky, maintains complexity
2. **Use PortalShell with modifications** - Still constraining
3. **Selected: New email layout** - Clean separation, full design control

**Implementation**:
- Create `/layouts/email.vue` for email-specific layout
- Set `definePageMeta({ layout: 'email' })` in email.vue
- Email layout will have its own minimal header with back-to-dashboard link

### Decision 3: Compact Modal Action Buttons

**What**: Replace large footer buttons with compact, icon-first actions

**Why**:
- Gmail uses small icon buttons with labels
- Reduces visual weight
- Feels more professional
- Saves screen space

**Design Pattern**:
```vue
<!-- Before: Large buttons -->
<button class="footer-button footer-button-primary">
  <Icon /> Antworten
</button>

<!-- After: Compact buttons -->
<div class="modal-actions-compact">
  <button class="action-btn action-reply" title="Antworten">
    <Icon size="18" /> Antworten
  </button>
  <button class="action-btn" title="Weiterleiten">
    <Icon size="18" /> Weiterleiten
  </button>
  <!-- More actions in dropdown menu -->
  <div class="action-dropdown">...</div>
</div>
```

**Button Sizing**:
- Height: 36px (down from ~48px)
- Padding: 8px 16px (down from 12px 20px)
- Icon size: 18px (down from 20px)
- Font size: 14px (down from 16px)

### Decision 4: Full-Width Email List Layout

**What**: Utilize full viewport width for email list (no left sidebar)

**Why**:
- More emails visible without scrolling
- Longer subject lines visible
- Modern email client standard
- Better use of widescreen monitors

**Layout Grid**:
```
┌─────────────────────────────────────────────────────────┐
│  📧 E-Mail    [Search...]         [+ Verfassen]         │ ← Top bar
├─────────────────────────────────────────────────────────┤
│  📥 Posteingang  ⭐ Markiert  📤 Gesendet  📝 Entwürfe   │ ← Tabs
├─────────────────────────────────────────────────────────┤
│  [✓] [Sort ▾]                          1-50 von 143     │ ← Controls
├─────────────────────────────────────────────────────────┤
│  ☐ ⭐  Dr. Sarah Mitchell   Vertragsprüfung...    2h     │
│  ☐ ☆  James Chen           Zeugenaussage...       5h     │
│  ...                                                      │
└─────────────────────────────────────────────────────────┘
```

### Decision 5: Responsive Navigation Strategy

**What**: 
- Desktop: Horizontal tabs for folders + dropdown for labels
- Tablet: Collapsible tabs + dropdown
- Mobile: Hamburger menu with drawer

**Why**: Maintains usability across all screen sizes

**Breakpoints**:
- Desktop: ≥1024px - Full horizontal tabs
- Tablet: 768px-1023px - Compressed tabs
- Mobile: <768px - Hamburger menu

## Risks / Trade-offs

### Risk 1: User Adaptation
**Risk**: Users accustomed to current sidebar may be confused
**Mitigation**: 
- Add subtle onboarding tooltip on first visit
- Include "What's New" announcement
- Pattern is familiar from Gmail (reduces learning curve)

### Risk 2: Mobile Navigation Complexity
**Risk**: Horizontal navigation may be cramped on small screens
**Mitigation**: 
- Implement hamburger menu for mobile
- Prioritize most-used folders in mobile view
- Test on multiple device sizes

### Risk 3: Development Scope
**Risk**: Full redesign may take longer than expected
**Mitigation**: 
- Break into phases (layout first, then polish)
- Use existing CSS variables and patterns where possible
- Reuse existing components (email items, modals) where functional

## Migration Plan

### Phase 1: Layout Foundation (Week 1)
1. Create new email layout without PortalShell
2. Implement basic top bar with back-to-dashboard link
3. Add horizontal folder tabs
4. Maintain existing email list and modal functionality

### Phase 2: Navigation Refinement (Week 1-2)
1. Add label filtering (dropdown or chips)
2. Integrate search into top bar
3. Implement responsive navigation
4. Test cross-browser compatibility

### Phase 3: Visual Polish (Week 2)
1. Refine modal footer buttons
2. Optimize spacing and typography
3. Add smooth transitions
4. Conduct user testing

### Rollback Strategy
- Keep old email.vue as email.vue.backup
- Feature flag: Enable new design for beta users first
- If critical issues: revert via git and redeploy

## Open Questions

1. **Should we keep labels visible by default or in a dropdown?**
   - Proposed: Dropdown to save space, since folders are primary navigation

2. **How should we handle the compose modal?**
   - Proposed: Keep existing modal, but trigger from top-right button

3. **Should folders have icons or just text labels?**
   - Proposed: Icons + text for clarity (consistent with current design)

4. **Do we need a separate mobile app bar?**
   - Proposed: Yes, simplified version with hamburger menu and compose button
