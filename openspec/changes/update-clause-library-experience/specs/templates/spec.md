## ADDED Requirements
### Requirement: Clause Sidebar Surfaces Authoritative Clauses
Clause sidebar MUST show user clauses from `/api/documents/clauses` and provide a fallback list of curated legal snippets when the API responds with zero items or an error.

#### Scenario: Clauses Available From API
- **GIVEN** the clauses API returns one or more records for the user
- **WHEN** the templates page loads
- **THEN** the sidebar shows those clause titles and descriptions without placeholder copy

#### Scenario: No Clauses Available
- **GIVEN** the API returns an empty list or fails
- **WHEN** the templates page loads
- **THEN** the sidebar shows a curated German-law fallback clause list clearly marked as suggestions

### Requirement: Users Can Create Clauses Inline
Templates page MUST allow creating a clause using existing `/api/clauses` endpoint without leaving the page.

#### Scenario: Clause Created
- **GIVEN** the user provides a clause title and body and confirms creation
- **WHEN** the modal submission succeeds
- **THEN** the new clause appears in the sidebar without a full page reload

### Requirement: Intro Actions Stay Relevant
Templates intro bar MUST exclude dead filter buttons and instead surface active actions.

#### Scenario: User Opens Templates Page
- **WHEN** the templates page loads
- **THEN** only functional actions (import, create template, create clause) are shown in the intro actions area
