## Why
- Clause library sidebar currently shows placeholder data and cannot add new clauses, leaving the section useless for document prep.
- Templates page still exposes a dead "Filtern" control and static highlight cards that confuse users about catalog status.
- Users requested a streamlined flow that surfaces real clause data, graceful fallbacks, and inline creation without breaking existing template actions.

## What Changes
- Remove the unused filter control and repurpose the actions area to focus on import and creation workflows.
- Drive highlight/metric cards from live catalog insights or template data as a fallback so the copy reflects the current repository.
- Enhance the clause rail to (a) hydrate from `/api/documents/clauses`, (b) surface curated fallback German-law snippets when empty, and (c) let users add new clauses inline.
- Provide a lightweight modal + API bridge to create clauses and refresh the sidebar without reloading the page.

## Impact
- Templates landing page reflects accurate counts and removes confusing dead UI.
- Clause widgets become functional: real data shown when available; informative legal fallbacks appear otherwise; new clauses can be created immediately.
- No backwards-incompatible API changes; relies on existing `/api/clauses` endpoints.

## Risks
- Clause creation modal must validate input to avoid empty records.
- Fallback clauses should be clearly marked to avoid implying persisted data.

## Rollback
- Revert the frontend changes in `pages/templates.vue` and remove any new styles.
- No database migrations required.
