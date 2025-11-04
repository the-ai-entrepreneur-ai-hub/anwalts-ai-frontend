# Email Interface Redesign - Migration Guide

## Overview

This document provides migration notes for the email interface redesign implemented on **October 15, 2025**.

## What Changed

### Major Changes

1. **Removed PortalShell Wrapper**
   - Email page now uses dedicated `email` layout
   - No more duplicate navigation bars
   - Back-to-dashboard link integrated into email top bar

2. **Horizontal Navigation**
   - Folder navigation moved from left sidebar to horizontal tabs below top bar
   - Labels accessible via dropdown menu
   - Full-width layout maximizes email viewing area

3. **Compact Modal Buttons**
   - Email modal footer buttons reduced from 48px to 36px height
   - Icon-first design with better spacing
   - Primary action (Reply) visually distinct

4. **Responsive Improvements**
   - Hamburger menu for mobile (<768px)
   - Collapsible navigation for tablet (768-1023px)
   - Optimized email list for all screen sizes

### Files Modified

| File | Change Type | Description |
|------|-------------|-------------|
| `pages/email.vue` | Complete rewrite | New Gmail-style interface |
| `layouts/email.vue` | Created | Email-specific layout without PortalShell |
| `pages/email.vue.backup-before-redesign` | Created | Backup of original implementation |

## Breaking Changes

### Layout System

**Before:**
```vue
<template>
  <PortalShell>
    <div class="email-app">
      <!-- sidebar + email list -->
    </div>
  </PortalShell>
</template>

<script setup>
definePageMeta({ layout: false })
</script>
```

**After:**
```vue
<template>
  <div class="email-app-container">
    <!-- top bar + horizontal tabs + email list -->
  </div>
</template>

<script setup>
definePageMeta({ layout: 'email' })
</script>
```

### Navigation Structure

**Before:** Left sidebar with vertical folder list
**After:** Horizontal tabs below top bar

### CSS Classes Removed

The following CSS classes were removed and should not be referenced:
- `.email-sidebar`
- `.folder-nav`
- `.folder-button`
- `.labels-section`
- `.sidebar-divider`

### CSS Classes Added

New classes for the redesigned interface:
- `.email-top-bar`
- `.email-nav-tabs`
- `.nav-tab`
- `.labels-dropdown-container`
- `.email-action-bar`
- `.modal-footer-compact`
- `.action-btn`

## Migration Steps

### For Developers

1. **Update any email page references:**
   ```javascript
   // If you were manually navigating to email:
   navigateTo('/email')  // Still works!
   ```

2. **Update any custom styles:**
   - If you have custom CSS targeting email page elements, review the new class names
   - Check `pages/email.vue` for the complete new structure

3. **Test responsive behavior:**
   - Test on mobile (<768px) to ensure hamburger menu works
   - Test on tablet (768-1023px) for navigation behavior
   - Test on desktop (≥1024px) for full horizontal tabs

### For Content/QA Team

1. **User flows to test:**
   - [ ] Email consent flow → Connect Gmail/Outlook
   - [ ] Browse folders (Posteingang, Markiert, Gesendet, etc.)
   - [ ] Filter by labels (dropdown menu)
   - [ ] Search emails
   - [ ] Open email detail modal
   - [ ] Reply, Forward, Archive, Delete actions
   - [ ] Settings modal
   - [ ] Mobile navigation (hamburger menu)

2. **Visual QA checklist:**
   - [ ] No duplicate navigation bars
   - [ ] Horizontal folder tabs visible and functional
   - [ ] Labels accessible via dropdown
   - [ ] Email modal footer buttons are compact (not oversized)
   - [ ] Smooth hover effects on all interactive elements
   - [ ] Mobile menu slides in from left
   - [ ] All breakpoints render correctly

## Responsive Breakpoints

| Breakpoint | Width | Behavior |
|------------|-------|----------|
| Mobile | <768px | Hamburger menu, simplified email list |
| Tablet | 768-1023px | Compressed tabs, some columns hidden |
| Desktop | ≥1024px | Full horizontal tabs, all columns visible |

## User Impact

### Positive Changes
- ✅ Familiar Gmail-like navigation
- ✅ More screen space for email content
- ✅ Cleaner, more professional appearance
- ✅ Better mobile experience
- ✅ Faster email scanning with optimized layout

### Learning Curve
- 📘 Users need to find folders in horizontal tabs instead of sidebar
- 📘 Labels now in dropdown (not always visible)
- **Mitigation**: Gmail-familiar pattern reduces confusion

## Rollback Plan

If critical issues are discovered:

1. **Restore original:**
   ```bash
   cp pages/email.vue.backup-before-redesign pages/email.vue
   ```

2. **Remove email layout:**
   ```bash
   rm layouts/email.vue
   ```

3. **Rebuild:**
   ```bash
   npm run build
   ```

4. **Deploy**

## Performance Notes

- **Initial load:** No significant change
- **Render time:** Slightly improved due to simpler DOM structure
- **Mobile performance:** Improved with optimized responsive design
- **Bundle size:** Email CSS reduced from ~23KB to ~22KB (gzipped: ~4KB)

## Support

For questions or issues:
1. Check this migration guide
2. Review the design document: `openspec/changes/redesign-email-interface/design.md`
3. Contact the development team

## Version

- **Implementation Date:** October 15, 2025
- **Change ID:** `redesign-email-interface`
- **Status:** ✅ Implemented
