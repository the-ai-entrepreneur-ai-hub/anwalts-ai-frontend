## ADDED Requirements

### Requirement: Documents Page Design Consistency
The Documents page UI SHALL present a consistent, uncluttered layout that keeps existing behavior intact and removes legacy modal styling.

#### Scenario: Consistent template navigation
- WHEN the user clicks the toolbar button `Vorlagen` OR the inline link `Alle Vorlagen öffnen`
- THEN the app navigates to `/templates?origin=documents` (optionally with `templateId` when present)

#### Scenario: No legacy modal styling present
- WHEN inspecting the page stylesheet
- THEN no `.modal-*` or `.template-card*` selectors remain in `anwalts-frontend-new/pages/documents.vue`

#### Scenario: Action footer never overlaps
- WHEN viewing at ≤768px and ≥1024px widths
- THEN the action footer spacing is sufficient so controls are visible and do not overlap the chat widget or preview content

#### Scenario: Accessible focus states
- WHEN focusing buttons, links, and chips on the Documents page
- THEN a visible focus outline appears and meets WCAG AA contrast for focus indicators

#### Scenario: Responsive inline templates grid
- WHEN the viewport shrinks to mobile widths
- THEN the inline templates quick-pick rearranges without horizontal overflow or overlap
