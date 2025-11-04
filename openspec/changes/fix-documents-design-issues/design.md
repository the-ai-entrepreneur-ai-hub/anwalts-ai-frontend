## Context
The Documents page mixes modern styling with legacy modal remnants and relatively heavy density (44px controls, deep shadows). Reports mention oversized bars and crowded elements. Functionality must remain unchanged; this is a UI consistency pass.

## Goals / Non-Goals
- Goals:
  - Remove dead CSS tied to the old modal and legacy template tiles.
  - Normalize spacing/density to match the rest of the portal (no “giant bars”).
  - Keep all behaviors intact: upload, clauses, quick-pick, generate.
  - Ensure both template triggers route to Templates consistently.
- Non-Goals:
  - No rewrite to reactive Vue for the entire page.
  - No changes to backend endpoints.

## Decisions
- Keep CSS variables as single source of truth; adjust spacing via small token-like values within this file.
- Remove `.modal-search` and `.template-card*` blocks; they are unused by the inline quick-pick.
- Leave inline quick-pick in place; maintain “navigate to Templates” behavior on both triggers.
- Wrap the dev error overlay (fixed red box) in a development guard, or remove it.

## Risks / Trade-offs
- Risk: Small spacing tweaks could affect perceived alignment in some browsers.
  - Mitigation: Validate at common breakpoints and revert quickly if needed (single-file change).
- Risk: Removing dead CSS could break any undiscovered references.
  - Mitigation: We confirmed current inline quick-pick uses `inline-template-*` classes. The removed blocks are not referenced by markup.

## Migration Plan
1) Remove dead CSS selectors.
2) Tweak spacing and density; keep changes minimal.
3) Validate at key breakpoints and with primary flows.
4) Rebuild frontend and redeploy.
5) Rollback by reverting documents.vue if any regressions appear.

## Open Questions
- Should we unify control heights (from 44px to 40px) across the entire product now, or only scope this to the Documents page?
- Is a small inline search for templates desired (without modal), or keep only the quick-pick + navigation?
