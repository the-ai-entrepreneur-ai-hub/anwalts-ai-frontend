## ADDED Requirements

### Requirement: Template Catalog Renders Backend Data
The Templates page MUST source its grid, search index, and quick actions from authenticated backend responses, not baked-in sample data.

#### Scenario: Authenticated load succeeds
- **GIVEN** an authenticated user with stored templates in the database
- **WHEN** they open `/templates`
- **THEN** the page requests `/api/templates`
- **AND** the UI renders exactly the records returned (titles, categories, updated timestamps) without placeholder rows

#### Scenario: No templates configured
- **GIVEN** the backend responds with an empty array
- **WHEN** the page renders
- **THEN** the skeleton transitions to an “empty” state that invites import/create actions
- **AND** no sample templates appear

#### Scenario: Backend error
- **GIVEN** `/api/templates` returns a 5xx or network failure
- **WHEN** the page loads
- **THEN** the UI surfaces an inline error banner/toast with retry
- **AND** the catalog does not display stale data from previous loads

### Requirement: Template CRUD Actions Persist Changes
Template create, update, duplicate, and delete actions MUST call the FastAPI endpoints, respect optimistic concurrency via `updated_at`, and reflect results in the client cache immediately.

#### Scenario: Create template succeeds
- **GIVEN** a user submits the create modal with valid data
- **WHEN** the frontend calls `POST /api/templates`
- **THEN** the response body (including `id`, `updated_at`) is merged into the in-memory list in order of recency

#### Scenario: Update conflict detected
- **GIVEN** another session has modified a template
- **WHEN** the user attempts to save edits with a stale `updated_at`
- **THEN** the backend returns 409
- **AND** the UI shows a conflict message prompting refresh before retrying

#### Scenario: Delete removes entry
- **GIVEN** a user confirms deletion
- **WHEN** `DELETE /api/templates/{id}` responds 200
- **THEN** the template disappears from the grid without reloading the entire page

### Requirement: Template Insights Reflect Live Usage
Dashboard tiles (highlight cards, suggested templates, “most used” chips) MUST consume dynamic metrics provided by the backend insights endpoint.

#### Scenario: Insights no data fallback
- **GIVEN** `/api/templates/insights` returns zero counts
- **WHEN** the page renders highlight cards
- **THEN** it displays neutral placeholders (e.g., “Keine Daten”) instead of hard-coded percentages

#### Scenario: Suggested template selection
- **GIVEN** the insights payload includes suggested templates with match scores
- **WHEN** the user clicks “Verwenden” from the suggestions rail
- **THEN** the corresponding template id is handed off to the Documents page using the same mechanism as the main grid

#### Scenario: Metrics update after CRUD
- **GIVEN** a new template is added or removed
- **WHEN** the operation completes
- **THEN** subsequent insights requests reflect the new counts
- **AND** the UI refreshes the cards without requiring a full reload
