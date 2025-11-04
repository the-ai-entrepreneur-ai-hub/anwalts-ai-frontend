# Proposal: Add Template Import Workflow

## Overview
The Templates library still shows a cramped “Neue Vorlage” modal on desktop, and the “Importieren” CTA is a stub that only fires a toast. We need a polished import flow that extracts uploaded documents, generates a starter template with AI, and folds it into the user’s catalogue—all without breaking existing CRUD behaviour.

## Goals
- Resize and polish the template create/edit modal so it matches the rest of the portal’s surface design on desktop and mobile.
- Replace the import placeholder with an end-to-end workflow: upload document → send to backend → AI derives title/content → new template appears in the catalogue.
- Provide clear user feedback (loading, success, failure) throughout the import process.

## Non-Goals
- No edits to the Documents page template picker (already addressed separately).
- No changes to clause import or other unrelated catalogue features.
- No new AI provider integrations beyond the existing sidecar/Together abstractions.

## Approach
- Update modal sizing tokens (min/max width, padding, scroll behaviour) and ensure responsive breakpoints keep the form usable.
- Add an “Importieren” flow on the templates page:
  - Show file picker, limit size/types, surface preview/loading state while import runs.
  - Call a new Nuxt server route (`POST /api/templates/import`) that proxies to a FastAPI endpoint.
- Backend:
  - Extend FastAPI with `/api/templates/import` accepting `multipart/form-data`.
  - Reuse `upload_processor` to sanitize the document, ask `AIService` for a template title/sections, then persist through `Database.create_template`.
  - Return the created template (ID, timestamps) so the frontend can merge it.
- Add defensive logging, meaningful errors, and unit/e2e coverage for the new flows.

## Impact
- UX: modal feels intentional; import CTA becomes productive.
- Ops: new endpoint uses existing storage + AI infrastructure; no schema change required.
- Risk: Medium—touches both frontend and backend critical paths but reuses existing primitives (upload processor, templates CRUD).

## Rollout & Validation
- Update Playwright coverage for modal sizing snapshot + import happy path.
- Add backend unit/integration tests for the import endpoint (success + failure).
- Manual smoke on staging: upload DOCX/PDF, confirm template appears and is editable.
- Deploy via existing Docker workflow (`docker compose up -d --no-deps --build frontend backend`, nginx reload).
