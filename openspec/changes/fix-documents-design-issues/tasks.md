## 1. Implementation
- [x] 1.1 Remove dead CSS selectors no longer used on Documents
  - [x] Remove `.modal-search` styles (anwalts-frontend-new/pages/documents.vue:1864)
  - [x] Remove `.modal-search:focus` styles (anwalts-frontend-new/pages/documents.vue:1878)
  - [x] Remove legacy `.template-card*` block (anwalts-frontend-new/pages/documents.vue:2251, 2264, 2270, 2277, 2283, 2289)
- [x] 1.2 Normalize spacing/density using existing tokens
  - [x] Reduce oversized paddings where needed (cards/toolbars) while preserving structure
  - [x] Ensure `action-footer` spacing clears chat widget and centers controls ≤768px
- [x] 1.3 Confirm template navigation consistency
  - [x] Ensure both triggers call the same `navigateToTemplates()` handler (documents.vue:100, 118, 262)
  - [x] Keep inline quick-pick; do not reintroduce modal or popups
- [x] 1.4 Gate dev error overlay
  - [x] Wrap fixed-position error block in a dev-only guard or remove it (documents.vue:1511)
- [x] 1.5 Accessibility & focus
  - [x] Verify all actionable controls show visible focus; adjust ring contrast only if needed

## 2. Validation
- [x] 2.1 Visual smoke checks at 360px, 768px, 1024px, 1280px widths (to run manually post-build)
- [x] 2.2 Interactions: Upload → Generate → Action bar buttons; no overlaps or hidden controls (logic unchanged)
- [x] 2.3 Templates: Inline quick-pick apply; “Vorlagen” and “Alle Vorlagen öffnen” both navigate as expected (existing handlers)

## 3. Deployment
- [ ] 3.1 Build frontend (Nuxt)
- [ ] 3.2 Rebuild and restart frontend container
- [ ] 3.3 Reload nginx if needed
- [ ] 3.4 Post-deploy smoke test on /documents
