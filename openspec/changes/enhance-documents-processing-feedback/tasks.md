## 1. Backend integration
- [x] 1.1 Ensure document generation endpoints invoke PIWI sanitization for instructions + uploads before Together AI calls
- [x] 1.2 Include sanitized metadata + new `processing_state` in responses consumed by frontend proxy
- [x] 1.3 Align /api/documents/save to return the persisted document id, status, and download URLs

## 2. Frontend experience
- [x] 2.1 Implement shared proxy composable/server route so generate & send buttons hit the same backend pathway with auth cookies
- [x] 2.2 Add preview overlay spinner + status text that toggles between “processing” and “generated” states
- [x] 2.3 Wire feedback toolbar visibility to real backend results; ensure copy/download/feedback buttons bind to saved document id
- [x] 2.4 Surface Together/PIWI errors inline without breaking existing layout or styling

## 3. Validation & deployment
- [x] 3.1 Add E2E/Nitro test covering spinner state, sanitized metadata display, and toolbar activation
- [x] 3.2 Rebuild + restart affected frontend/backend containers
- [x] 3.3 Smoke test document upload → generation → download flow post-deploy
