## MODIFIED Requirements

### Requirement: Settings Overview Provides Live Analytics
The admin overview MUST surface live organization KPIs, trend charts, and service health sourced from production data, and the KPI totals MUST reconcile with the canonical entity endpoints.

#### Scenario: Admin requests overview metrics
- **GIVEN** an authenticated admin
- **WHEN** they call `GET /api/settings/overview`
- **THEN** the response includes KPI totals with week-over-week deltas for users, documents, cases, and API calls
- **AND** includes daily time-series for user growth and API usage covering the last 30 days
- **AND** includes system-health entries for database, cache, AI, and web servers with current status/uptime percentages derived from telemetry.

#### Scenario: Overview data refresh updates timestamp
- **GIVEN** the settings page shows a last-updated timestamp
- **WHEN** the admin clicks "Aktualisieren"
- **THEN** the frontend refetches `GET /api/settings/overview`
- **AND** renders the new metrics and timestamp without reloading the page.

#### Scenario: KPI totals reconcile with entity endpoints
- **GIVEN** the overview shows KPI totals for active users, documents, cases, and API calls
- **WHEN** the admin cross-checks with `GET /api/settings/users`, `GET /api/settings/api/tokens`, and other companion endpoints
- **THEN** the totals in the overview match the aggregated counts from the respective endpoints (allowing a maximum delta of ±1 caused by in-flight writes).

## ADDED Requirements

### Requirement: Settings interactions wait for backend hydration
The settings UI MUST withhold interactivity until the required backend data is loaded and keep UI state synchronized after mutations.

#### Scenario: Preferences toggles remain disabled until data loads
- **GIVEN** an admin opens the "Allgemeine Einstellungen" tab
- **WHEN** `GET /api/settings/preferences` is still pending
- **THEN** the language, timezone, and security toggles render in a loading state and cannot be changed yet
- **AND** once the request resolves, the toggles adopt the returned values before becoming interactive.

#### Scenario: User and API tables refresh after mutations
- **GIVEN** the admin revokes an API key or toggles a user
- **WHEN** the corresponding `DELETE /api/settings/api/tokens/{id}` or `POST /api/settings/users/{id}/toggle` call succeeds
- **THEN** the UI refetches the dependent list endpoint
- **AND** the row updates to mirror the backend response without showing stale placeholder data.

### Requirement: Settings layout adapts across admin breakpoints
The settings layout MUST remain legible and usable from mobile to desktop breakpoints without overflow or clipped controls.

#### Scenario: Mobile viewport stacks content accessibly
- **GIVEN** the viewport width is ≤ 414px
- **WHEN** an admin visits the settings page
- **THEN** the header, toolbars, and KPI cards stack vertically with appropriate spacing
- **AND** tabular sections (users, API endpoints) provide horizontal scrolling or card views so controls remain reachable without overlapping.

#### Scenario: Desktop viewport preserves multi-column density
- **GIVEN** the viewport width is ≥ 1280px
- **WHEN** an admin visits the settings page
- **THEN** the KPI grid renders in four columns, charts align side-by-side, and management tables use the available width without exceeding the container or causing text truncation.
