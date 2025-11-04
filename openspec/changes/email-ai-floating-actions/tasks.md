# Tasks: Email AI Floating Actions

- [x] Define proposal and scope
- [ ] Backend: Add EmailReplyRequest and EmailToDocumentRequest models
- [ ] Backend: Implement POST /api/email/reply with rate limit and Gmail fetch reuse
- [ ] Backend: Implement POST /api/email/to-document with AI document generation + save
- [ ] Frontend: Add floating action container in email.vue (visible when an email is open)
- [ ] Frontend: Wire Generate Response button to /api/email/reply, render draft and actions
- [ ] Frontend: Wire Generate Document button to /api/email/to-document, show link/toast
- [ ] Frontend: Loading/disabled states and error toasts
- [ ] Verify Together+sidecar work; handle 429 gracefully
- [ ] Build, redeploy backend/frontend, reload nginx
- [ ] Smoke test: open email → reply draft → compose; email → document → open

## Acceptance Checklist
- [ ] Buttons appear only with selected email, non-intrusive UI
- [ ] Reply returns content and can be copied/inserted to compose
- [ ] Document is created and accessible with returned id/links
- [ ] No regressions for existing summarize/sync/list flows

