## Why
- The Documents page layout has inconsistent spacing, oversized controls, and legacy modal CSS that create visual clutter and confusion. Users reported “bars look too big,” and action elements felt crowded.
- Dead CSS from the old templates modal and unused styles increases bundle size and complicates maintenance.
- Both the toolbar “Vorlagen” button and the inline “Alle Vorlagen öffnen” link should behave identically and navigate to the Templates page; this behavior exists but isn’t documented or tested.

## What Changes
- Normalize spacing and density across the Documents page (cards, toolbars, inline lists, action bar) using small token adjustments. Keep the existing visual language but reduce overbearing shadows/padding to improve readability.
- Remove legacy, unused modal CSS and stale template card styles from the page stylesheet to reduce size and avoid future confusion.
- Ensure both template navigation triggers use the same route and add clear, consistent labels with accessible focus states.
- Guard developer-only error overlays so users never see raw error blocks on production.
- Improve responsive behavior for the left form pane and right preview pane at common breakpoints (≤768px, 768–1024px, ≥1024px) so controls don’t collide or wrap awkwardly.

## Impact
- Frontend only; focused changes in `anwalts-frontend-new/pages/documents.vue`.
- Behavior of “Vorlagen” remains navigate-to-Templates; the inline quick-pick stays but is visually tidied (no modal).
- No backend changes required.

## Affected Code
- anwalts-frontend-new/pages/documents.vue
  - Remove dead CSS: `modal-search` and `template-card` blocks
    - anwalts-frontend-new/pages/documents.vue:1864
    - anwalts-frontend-new/pages/documents.vue:1878
    - anwalts-frontend-new/pages/documents.vue:2251
    - anwalts-frontend-new/pages/documents.vue:2264
    - anwalts-frontend-new/pages/documents.vue:2270
    - anwalts-frontend-new/pages/documents.vue:2277
    - anwalts-frontend-new/pages/documents.vue:2283
    - anwalts-frontend-new/pages/documents.vue:2289
  - Keep inline templates quick-pick; verify navigation triggers:
    - anwalts-frontend-new/pages/documents.vue:100
    - anwalts-frontend-new/pages/documents.vue:118
    - anwalts-frontend-new/pages/documents.vue:262
  - Tidy action footer spacing to avoid overlap and ensure centered layout on narrow screens:
    - anwalts-frontend-new/pages/documents.vue:2163
    - anwalts-frontend-new/pages/documents.vue:2171
    - anwalts-frontend-new/pages/documents.vue:2422
    - anwalts-frontend-new/pages/documents.vue:2946
  - Remove/gate dev-only fixed-position error overlay:
    - anwalts-frontend-new/pages/documents.vue:1511

## Acceptance Criteria
- Spacing
  - Cards, toolbars, and quick-pick items use consistent gaps; content no longer appears cramped or “stacked”.
  - Action footer spacing is consistent and does not overlap chat widgets; buttons remain reachable on all breakpoints.
- Consistency
  - Both “Vorlagen” triggers navigate to `/templates` with `?origin=documents` and optional `templateId` when present.
  - Legacy modal styles are removed; no CSS selectors for `.modal-*` or `.template-card*` remain in the file.
- Accessibility
  - All interactive elements show visible focus outlines; color contrast meets AA for text and focus rings.
- Responsiveness
  - ≤768px: controls stack with centered primary action; inline templates grid flows without overflow.
  - ≥1024px: two-column layout remains stable without vertical overflow or awkward scroll cuts.
- No behavior regressions in document upload, clause chips, template inline quick-pick, or generation flow.

## Non‑Goals
- No migration from the current DOM-driven scripting to a fully reactive Vue component (out of scope).
- No changes to backend APIs or data models.
- No significant visual redesign; keep the existing look and feel, just correct spacing/density issues and remove dead code.

## Rollout
- Implement CSS and small template adjustments behind a single PR.
- Rebuild the frontend container and perform a quick smoke test for Documents.
- If any visual regressions are reported, rollback by reverting the single file change.
