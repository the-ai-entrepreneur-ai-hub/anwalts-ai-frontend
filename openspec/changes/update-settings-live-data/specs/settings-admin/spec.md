## ADDED Requirements

### Requirement: Settings Overview Provides Live Analytics
The admin overview MUST surface live organization KPIs, trend charts, and service health sourced from production data.

#### Scenario: Admin requests overview metrics
- **GIVEN** an authenticated admin
- **WHEN** they call `GET /api/settings/overview`
- **THEN** the response includes KPI totals with week-over-week deltas for users, documents, cases, and API calls
- **AND** includes daily time-series for user growth and API usage covering the last 30 days
- **AND** includes system-health entries for database, cache, AI, and web servers with current status/uptime percentages.

#### Scenario: Overview data refresh updates timestamp
- **GIVEN** the settings page shows a last-updated timestamp
- **WHEN** the admin clicks "Aktualisieren"
- **THEN** the frontend refetches `GET /api/settings/overview`
- **AND** renders the new metrics and timestamp without reloading the page.

### Requirement: API Token Management Is Backed by Secure Storage
Admins MUST manage API tokens without exposing raw secrets after creation and audit token usage.

#### Scenario: Admin creates an API token
- **WHEN** the admin submits `POST /api/settings/api/tokens` with an expiry window
- **THEN** the backend persists a hashed token with last4, expiry, and owner metadata
- **AND** returns the plain token exactly once in the response
- **AND** the settings page prepends the new token to the list with creation/usage metadata.

#### Scenario: Admin revokes an API token
- **WHEN** the admin triggers revoke on a listed token
- **THEN** the frontend calls `DELETE /api/settings/api/tokens/{id}`
- **AND** the backend marks the token revoked and removes it from subsequent list responses.

### Requirement: API Endpoint Metrics Reflect Live Traffic
Request metrics MUST be derived from real traffic and provide latency + rate insights per endpoint/method.

#### Scenario: Metrics endpoint aggregates recent traffic
- **WHEN** the admin calls `GET /api/settings/api/endpoints`
- **THEN** the response includes each public API path/method pair the middleware observed in the last 7 days
- **AND** each record provides total calls, average latency (ms), and peak per-minute throughput derived from stored metrics.

### Requirement: Webhook Registry Supports CRUD and Testing
Admins MUST manage outbound webhooks and inspect recent delivery logs.

#### Scenario: Admin creates a webhook
- **GIVEN** a payload with name, URL, events, and status
- **WHEN** the admin submits `POST /api/settings/webhooks`
- **THEN** the backend validates the URL, stores the webhook, and returns the persisted model with generated id
- **AND** the frontend updates the list without reload.

#### Scenario: Admin tests a webhook delivery
- **WHEN** the admin clicks "Testen" for a webhook
- **THEN** the frontend calls `POST /api/settings/webhooks/{id}/test`
- **AND** the backend sends a signed sample payload to the webhook URL and records the response status in `webhook_logs`
- **AND** the latest logs refresh in the UI.

### Requirement: User Administration Reflects Live Directory State
The settings page MUST list real users with role and active state controls.

#### Scenario: Admin toggles user activation
- **WHEN** the admin triggers the activate/deactivate control for a user via `POST /api/settings/users/{id}/toggle`
- **THEN** the backend updates `users.is_active` accordingly
- **AND** subsequent login attempts honor the new state
- **AND** the row state updates in the UI.

#### Scenario: Admin changes a user role
- **WHEN** the admin submits `POST /api/settings/users/{id}/role` with a target role
- **THEN** the backend validates permissions, updates the role, and returns the updated user so the table reflects the change.

### Requirement: Organization Preferences Persist and Drive UI Defaults
Platform-wide language, timezone, security toggles, and password policy MUST persist and hydrate the settings UI.

#### Scenario: Admin updates preferences
- **WHEN** the admin saves changes via `POST /api/settings/preferences`
- **THEN** the backend stores the new values in `organization_settings`
- **AND** `GET /api/settings/preferences` immediately reflects the updates for subsequent visits
- **AND** toggles such as two-factor requirement are exposed to other services via the same store.

### Requirement: Data Export Buttons Return Real Snapshots
Export buttons MUST trigger downloadable content for audit purposes.

#### Scenario: Admin downloads CSV export
- **WHEN** the admin clicks "CSV-Export"
- **THEN** the frontend calls `GET /api/settings/export.csv`
- **AND** the backend streams a CSV containing users, documents, templates, and webhooks with headers
- **AND** the browser saves the file without corrupting layout.

#### Scenario: Admin downloads JSON export
- **WHEN** the admin clicks "JSON-Export"
- **THEN** the frontend calls `GET /api/settings/export.json`
- **AND** receives a JSON snapshot packaging the same entities grouped by type.
