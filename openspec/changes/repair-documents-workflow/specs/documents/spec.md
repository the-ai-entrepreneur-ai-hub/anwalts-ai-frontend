## ADDED Requirements

### Requirement: Document Workflow Accepts Cookie or Bearer Auth
Document-related APIs MUST authenticate requests using either the backend-issued HTTP-only cookies (`auth_token`, `sid`, `sat`) or an explicit `Authorization: Bearer` header so browser clients can operate without exposing tokens in localStorage.

#### Scenario: Cookie-only browser call succeeds
- **GIVEN** a signed-in user with only the backend `auth_token` cookie set
- **WHEN** the client requests `/api/ai/generate-document` or `/api/documents/save`
- **THEN** the backend authenticates via cookie and returns 200 (not 401/403)
- **AND** the response body matches the documented schema

#### Scenario: Missing credentials fail fast
- **GIVEN** no cookies and no `Authorization` header
- **WHEN** the same endpoints are called
- **THEN** the backend responds with 401 and an actionable `detail` message without side-effects

### Requirement: Document UI Loads Dynamic Catalog Data
The documents page MUST fetch templates and clauses from backend APIs, fall back gracefully when unavailable, and avoid presenting stale hard-coded placeholder content as real data.

#### Scenario: Templates render from API
- **GIVEN** the backend returns a list of user templates
- **WHEN** the documents page loads
- **THEN** the modal card grid reflects the API data, including names, categories, and timestamps
- **AND** templates persist after refresh without relying on in-page constants

#### Scenario: Catalog failure shows helper state
- **GIVEN** the backend responds with 500
- **WHEN** the documents page requests templates or clauses
- **THEN** the UI displays a non-blocking error state (banner/toast) and disables dependent actions until retry

### Requirement: Together-backed Generation Returns Actionable Results
Legal document generation endpoints MUST surface Together API errors explicitly and only persist/save drafts when real model content is produced.

#### Scenario: Together returns non-2xx
- **GIVEN** Together responds with a non-2xx status to a generation request
- **WHEN** `/api/ai/generate-document-simple` is invoked
- **THEN** the backend propagates a 502/503 with the upstream error summary
- **AND** the frontend shows a retry prompt instead of the static “Ich konnte …” copy

#### Scenario: Successful generation contains metadata
- **GIVEN** Together returns a valid completion
- **WHEN** the backend responds
- **THEN** the payload includes the rendered HTML, `model_used`, `generation_time_ms`, sanitized instruction details, and redaction counts used for UI annotations
