# Proposal: Email AI Floating Actions (Reply & Document)

- Change ID: email-ai-floating-actions
- Owners: Platform AI / Frontend
- Status: Proposed
- Created: 2025-11-03

## Problem
Users can view emails but lack streamlined AI actions within the reading context. Common actions like “Generate response” or “Create document from email” require manual copy/paste and separate screens. This slows workflows and increases errors.

## Goals
- Add a floating actions container in the email reading view offering:
  - Generate Response (AI-drafted reply)
  - Generate Document (AI-generated legal document based on the email)
- Use existing AI service integration (Together/sidecar) with minimal new surface area.
- Keep UI responsive and non-intrusive; no modal popups beyond existing email modal.

## Non‑Goals
- Sending emails automatically.
- Changing the overall email UX/layout beyond the floating panel and buttons.
- Replacing existing summarize flow (it remains and is reused where possible).

## High‑Level Design
- Backend
  - New endpoints:
    - POST `/api/email/reply` → Generate a German legal reply draft given `email_id` or raw `subject/body`.
    - POST `/api/email/to-document` → Generate and save a legal document derived from the email, returning `documentId` and links.
  - Rate limiting (Redis) consistent with existing AI endpoints.
  - Reuse existing Gmail fetch helpers and AI service (Together or sidecar fallback).

- Frontend
  - Add a floating action container inside `pages/email.vue` shown when an email is open.
  - Buttons trigger backend endpoints and render results inline:
    - Reply: show draft, with Copy + “Use in reply” (opens compose prefilled).
    - Document: on success, show link to open the created document.
  - Maintain responsive behavior; no blocking modals.

## API Spec (Draft)
- POST `/api/email/reply`
  - body: `{ email_id?: string, subject?: string, body?: string, tone?: "legal"|"neutral"|"plain" }`
  - returns: `{ success: true, subject: string, reply: string, model?: string }`

- POST `/api/email/to-document`
  - body: `{ email_id?: string, subject?: string, body?: string, document_type?: string, title?: string }`
  - returns: `{ success: true, documentId: string, title: string, download?: { pdf?: string, docx?: string } }`

## Acceptance Criteria
- Floating actions show only when an email is selected.
- Generate Response returns a reply and displays it without page navigation.
- “Use in reply” opens compose with the draft prefilled.
- Generate Document creates and returns a saved document and provides an open/download link.
- Works with Together provider and sidecar fallback.

## Risks & Mitigations
- AI latency: show button loading states and non-blocking UI.
- Rate limits: surface clear error toast on 429.
- Gmail content failures: degrade gracefully with user message.

## Rollout
- Build and redeploy backend + frontend containers, reload nginx.
- Smoke test email open → reply draft → compose, and email → document creation.

