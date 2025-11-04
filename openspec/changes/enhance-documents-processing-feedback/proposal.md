## Why
- Lawyers report that the documents workspace feels unresponsive: the “Dokument erzeugen” and “Zur Verarbeitung senden” buttons do not trigger visible progress or backend work, so nothing appears to happen after instructions are entered.
- The preview pane lacks an in-place progress indicator; without a spinner and status copy inside the output container, users think the flow is frozen while Together AI is still generating content.
- Upload-assisted generations are not reliably sanitising instructions and file excerpts through the PIWI pipeline before Together AI receives them, leaving PII removal unverified and breaking trust in the feature.
- Post-generation controls (copy, Bewerten, edit, download) do not consistently appear or stay wired to saved documents, so users cannot act on the generated text.

## What Changes
- Rewire the documents page actions so both “Dokument erzeugen” and “Zur Verarbeitung senden” call the same Nuxt server proxy that attaches auth cookies, forwards to the Together-backed FastAPI endpoints, and waits for PIWI-sanitised responses.
- Add an explicit progress overlay in the preview container (animated circle with “Dokument wird erstellt …”) that activates while a generation or send request is in-flight and switches to success copy once content arrives.
- Ensure uploaded files run through the PIWI sanitizer before their excerpts reach Together AI, and propagate sanitized instruction metadata back to the preview for display.
- Gate the feedback toolbar (copy/like/dislike/edit/download) behind successful generations, reusing the current styling but guaranteeing the controls bind to the live document id returned from the backend.

## Impact
- Touches `anwalts-frontend-new/pages/documents.vue`, related composables/server routes, and FastAPI document handlers to guarantee sanitisation metadata is present.
- Requires coordinated frontend + backend deployment so the proxy route and response schema stay aligned; containers must be rebuilt/restarted.
- Adds new integration coverage for spinner states, Together/PIWI round-trips, and toolbar visibility; no external services beyond existing Together AI keys.
