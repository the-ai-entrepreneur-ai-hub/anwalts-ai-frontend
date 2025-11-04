# Email Interface Redesign Proposal

## Why

The current email section has critical design flaws that create a poor user experience:

1. **Duplicate Navigation Bars**: The page displays two navigation bars (PortalShell navigation + email sidebar navigation), creating visual clutter and confusion
2. **Poor Layout Structure**: Left sidebar navigation doesn't align with modern email client patterns (Gmail, Outlook)
3. **Oversized Action Buttons**: Email modal footer buttons are too large and visually overwhelming
4. **Non-professional Appearance**: The overall design doesn't meet professional standards expected in a legal software application

These issues significantly impact the user experience and professional credibility of the platform.

## What Changes

- **Remove duplicate navigation**: Eliminate the PortalShell wrapper or integrate email navigation properly
- **Redesign navigation layout**: Move folder/label navigation from left sidebar to horizontal top bar (Gmail-style)
- **Refactor email list view**: Create cleaner, more compact email list with better visual hierarchy
- **Redesign modal footer buttons**: Replace large buttons with smaller, icon-first actions similar to Gmail
- **Implement responsive design**: Ensure smooth transitions between desktop and mobile views
- **Improve visual consistency**: Align with professional email client standards (Gmail, Outlook, Apple Mail)
- **Optimize white space**: Better use of screen real estate with top navigation

## Impact

### Affected Specs
- `email-client` (new spec) - Complete email interface redesign

### Affected Code
- `/pages/email.vue` - Complete UI restructure
  - Remove PortalShell wrapper or create email-specific layout
  - Move sidebar navigation to top bar
  - Redesign email list layout
  - Refactor modal footer
- `/components/PortalShell.vue` - May need conditional rendering for email page
- `/layouts/` - Potentially create new `email.vue` layout

### User Experience Impact
- **Positive**: Cleaner, more professional interface
- **Positive**: Familiar Gmail-like navigation
- **Positive**: More screen space for email content
- **Positive**: Better visual hierarchy and reduced clutter
- **Migration**: Users will need to adapt to new navigation pattern (minimal learning curve due to Gmail familiarity)

### Technical Impact
- No breaking API changes
- Frontend-only changes
- No database schema changes
- Maintains existing functionality with improved UX
