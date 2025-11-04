## Why
- On viewports below ~960px the Templates DOM order renders the side rail before the catalog, forcing users to scroll past highlights before seeing templates (report: "page is not responsive").
- Between 960–1280px the fixed three-column grid (`templates-layout`) squeezes the main column below 560px and causes horizontal overflow for recommendation cards.
- The action bar and search inputs do not adapt to narrow widths, producing cramped buttons and clipped text on tablets.

## What Changes
- Introduce grid-area based layout so the main catalog stays first while rails stack beneath it on tablet/mobile.
- Add responsive breakpoints for the intro actions, metrics, and recommendation panels to prevent overflow and ensure full-width stacking when space is limited.
- Tighten template card grid min widths and spacing so cards reflow cleanly without truncation on small screens.

## Impact
- Frontend-only changes in `anwalts-frontend-new/pages/templates.vue` (template + style adjustments).
- No backend or schema updates.
- Requires rebuilding the frontend bundle and running targeted UI checks.
