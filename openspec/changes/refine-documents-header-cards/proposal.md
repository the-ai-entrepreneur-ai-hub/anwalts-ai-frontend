## Why
- The two status cards at the top of the Documents page (“Qualitätsscore” and “PDF‑Export”) look visually polished, but the information is cramped, lacks hierarchy, and feels static even after a document is generated.
- Lawyers expect these hero cards to summarise the current mandate state (word count, compliance notes, last update) and immediately signal whether anything needs their attention.
- Without structured content, the cards feel ornamental rather than functional, leading to the perception that the experience is unpredictable and not on par with European legal tools.

## What Changes
- Redesign both header cards so they follow a consistent information architecture: a leading badge/icon, a prominent primary metric, supporting sub-metrics, and a contextual footer hint.
- Surface dynamic data already available on the page (e.g., `qualityBadge`, `previewWordCount`, clause count, latest processing state/subtext) so the cards respond to user actions instead of presenting static copy.
- Add subtle progress cues (pulse, color transitions) that respect accessibility guidelines while clearly communicating whether the draft still needs review or export confirmation.

## Impact
- Frontend-only adjustments inside `anwalts-frontend-new/pages/documents.vue`; no backend changes or new endpoints.
- We may introduce a lightweight helper/composable for formatting status card data, but expect to keep logic inline with the page.
- Minor unit coverage update if helper logic is extracted; otherwise manual QA suffices.

## Affected Code
- `anwalts-frontend-new/pages/documents.vue` – restructure header card markup, bind dynamic data, adjust Tailwind classes for layout and state styles.
- `tests/frontend/documents-header-cards.spec.ts` (optional) – cover helper logic if extracted.

## Acceptance Criteria
- Each card presents content in the following structure: icon/badge, headline metric, two supporting rows, and a tasteful footer note.
- “Qualitätsscore” card reflects live draft state (word count + clause coverage) and visually distinguishes success vs pending vs attention-needed states.
- “PDF‑Export” card communicates status of latest export/save and shows timestamp or prompt to export; when no document exists it provides a contextual call-to-action.
- Layout remains responsive across breakpoints (≥360px) with consistent spacing and no content overlap.
- No regressions to existing generation, feedback, or export flows.

## Rollout
- Implement changes in a single PR/ticket.
- `npm run build` for Nuxt, restart frontend container, smoke-test `/documents`.
