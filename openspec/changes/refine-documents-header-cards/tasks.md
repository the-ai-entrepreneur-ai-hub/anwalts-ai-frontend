## 1. Preparation
- [x] 1.1 Review current header card markup (`documents.vue` header section) and note available reactive data (`qualityBadge`, `previewWordCount`, `processingState`, `processingSubtext`).

## 2. Implementation
- [x] 2.1 Refactor the “Qualitätsscore” card to include icon badge, headline metric, supporting stats (word/clause coverage), and contextual footer text bound to live data.
- [x] 2.2 Refactor the “PDF‑Export” card to surface latest export/save status (processing state, timestamp) with a structured layout and fallback CTA when no document exists.
- [x] 2.3 Ensure cards share a consistent grid/spacing system and adapt gracefully across breakpoints.

## 3. Testing
- [ ] 3.1 (Optional) Add targeted unit test if helper/computed extraction is created; otherwise document manual validation.

## 4. Validation
- [ ] 4.1 Manual QA on `/documents` at 360px, 768px, 1024px verifying responsive behaviour and dynamic content updates.

## 5. Deployment
- [x] 5.1 Build the frontend (`npm run build`).
- [x] 5.2 Restart frontend container (`docker compose up -d frontend`).
- [x] 5.3 Smoke-test live `/documents` after deploy.
