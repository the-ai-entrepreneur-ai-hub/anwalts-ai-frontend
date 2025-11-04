# Proposal: Update Template Navigation

## Overview
Documents page currently offers inline template toggling via “Vorlagen” and “Alle Vorlagen” controls. After recent fixes the inline list behaves, yet users still experience confusion—clicking either control should open the dedicated Templates area, but the UI keeps the user on the Documents page. We will align these entry points so both buttons route to the Templates page, while keeping inline quick picks as a secondary aid.

## Goals
- Make both “Vorlagen” (toolbar) and “Alle Vorlagen” (inline link) navigate to the `/templates` route.
- Preserve existing inline quick-pick rendering for immediate context without relying on modal/toggle state.
- Ensure templates chosen in the Templates page still pre-fill the Documents form via the existing handoff (query/localStorage).

## Non-Goals
- No redesign of the Templates page itself.
- No re-introduction of modal-based template selection.
- No changes to backend template APIs beyond verifying they remain reachable.

## Approach
- Replace the toggle handler with a navigation helper that routes users to `/templates?origin=documents`.
- Remove now-unused toggle state (`SHOW_ALL_TEMPLATES`) and ensure inline rendering gracefully handles full lists.
- Update DOM event bindings for both buttons to call the navigation helper and adjust accessibility attributes as needed.
- Run targeted smoke tests (unit/E2E) to confirm navigation + handoff polarity.

## Impact
- **Documents Page UX**: Users reach the comprehensive Templates section consistently.
- **Code Cleanup**: Removes unused toggle code, simplifying maintenance.
- **Risk**: Low; primarily front-end navigation changes. Regression mitigated through manual/automated checks.

## Rollout & Validation
- Local verification: `npx playwright test tests/e2e/templates-navigation.spec.ts` (new/updated).
- Smoke test on staging/preview: confirm toolbar + inline controls navigate correctly, and selected template returns to Documents with pre-filled fields.
- Deployment: Rebuild/restart frontend container; nginx reload as standard.
