# Design: Email AI Floating Actions

## UI
- Floating container inside email modal (`.modal-body`) anchored bottom-right.
- Buttons: primary (Generate Response), secondary (Generate Document).
- Action area below buttons renders reply draft preview and success link for document.
- States: idle, loading, success, error.

## Backend
- Reuse `_fetch_gmail_message_contents` to resolve email text.
- `POST /api/email/reply`
  - Compose a structured prompt for a formal German reply (“Sie”-Form), configurable tone.
  - `ai_service.generate_completion` with low temperature.
- `POST /api/email/to-document`
  - Build instructions from subject/body.
  - `ai_service.generate_document` → normalize JSON → save via `db.create_document`.
  - Return id + download links like `/api/documents/save`.

## Error Handling
- 401/403: surface “Bitte erneut verbinden/zugreifen” toast.
- 429: clear message about rate limiting.
- 5xx: generic “Aktion fehlgeschlagen” message, keep UI interactive.

