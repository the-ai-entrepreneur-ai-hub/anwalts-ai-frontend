# Dashboard Specification Delta

## MODIFIED Requirements

### Requirement: Dashboard Templates Display
The dashboard MUST display a templates section showing available document templates for quick access.

#### Scenario: Template List Display
- **WHEN** user loads the dashboard
- **THEN** system displays up to 6 templates in a responsive grid
- **AND** templates show real data from `/api/templates` endpoint
- **AND** template metadata includes: title, last update date, version, status, category

#### Scenario: Template Data Fetching
- **WHEN** dashboard mounts
- **THEN** system calls `GET /api/templates` with user authentication
- **AND** system stores template data in reactive state
- **AND** system displays templates in order returned by API (limited to first 6)

#### Scenario: Template Metadata Display
- **WHEN** templates are displayed
- **THEN** each template shows:
  - Template title or name
  - Last update date in German format ("DD. MMM YYYY")
  - Version number (if available)
  - Publication status ("Freigegeben" if published)
  - Category badge

#### Scenario: Dynamic Date Formatting
- **WHEN** template dates are displayed
- **THEN** system formats `updated_at` or `created_at` timestamp
- **AND** displays in German locale format (e.g., "15. Nov 2025")
- **AND** uses real timestamp from API (not hardcoded dates)

#### Scenario: Template Actions
- **WHEN** user clicks template "Erstellen" button
- **THEN** system navigates to `/assistant?template={template-id}`
- **AND** template context is passed to AI assistant

- **WHEN** user clicks template "Ansehen" button
- **THEN** system navigates to `/templates/{template-id}` detail page

#### Scenario: API Failure Graceful Degradation
- **WHEN** `/api/templates` endpoint fails or returns empty
- **THEN** system displays fallback static templates (6 hardcoded templates)
- **AND** user can still access template creation functionality
- **AND** no error messages disrupt user experience

#### Scenario: Loading State
- **WHEN** templates are being fetched
- **THEN** system shows loading skeleton (optional enhancement)
- **OR** system shows cached/fallback templates immediately

## REMOVED Requirements

### Requirement: Static Hardcoded Templates
**Reason**: Templates now fetched dynamically from API. Static templates remain only as fallback.

**Migration**: 
- Existing hardcoded template HTML (lines 207-291) moved to fallback `<template v-else>` block
- Primary template display now uses `v-for` loop with API data
- No user-facing changes - visual appearance identical

**Previous Behavior**:
- Dashboard displayed 6 hardcoded template divs
- Template dates hardcoded as "12. Aug 2025", "30. Jul 2025", etc.
- Template metadata (version, status) was fake/static
- Adding/removing templates required code changes

**New Behavior**:
- Dashboard fetches templates from `/api/templates`
- Template dates show real `updated_at` timestamps
- Template metadata reflects actual database values
- Templates update automatically when database changes

**Removed Code**:
```vue
<!-- REMOVED: Primary hardcoded templates (moved to fallback) -->
<div class="template-card">
  <div class="flex items-start justify-between">
    <div>
      <p class="font-medium">NDA – Standard (DE)</p>
      <p class="text-xs text-gray-500 mt-1">Letztes Update: 12. Aug 2025 · Freigegeben</p>
      <!--                                                   ^^^^^^^^^^^^^^^ -->
      <!--                                                   HARDCODED DATE -->
    </div>
    <span class="badge badge-primary">Vertrag</span>
  </div>
  <div class="mt-4 flex items-center gap-2">
    <button class="btn btn-primary" data-template="nda">Erstellen</button>
    <button class="btn btn-secondary">Ansehen</button>
  </div>
</div>
<!-- ... 5 more hardcoded templates ... -->
```

## ADDED Requirements

### Requirement: Template Data Fetching
The dashboard MUST fetch template data from the backend API on mount.

#### Scenario: Template API Integration
- **GIVEN** user is authenticated
- **WHEN** dashboard component mounts
- **THEN** system calls `GET /api/templates` with auth headers
- **AND** system parses response JSON
- **AND** system extracts `templates` array or root array from response
- **AND** system stores templates in reactive `templates` ref

#### Scenario: Template Data Structure
- **WHEN** templates are fetched from API
- **THEN** each template contains at minimum:
  - `id`: Unique identifier
  - `name` or `title`: Display name
  - `category`: Template category
  - `created_at`: Creation timestamp
- **AND** optionally contains:
  - `updated_at`: Last update timestamp
  - `version`: Version number or string
  - `status`: Draft or published status

### Requirement: Template Date Formatting Helper
The dashboard MUST provide a helper function to format ISO timestamps for display.

#### Scenario: German Date Formatting
- **GIVEN** a template with `updated_at` = "2025-11-15T10:30:00Z"
- **WHEN** system formats date for display
- **THEN** output is "15. Nov. 2025" (German locale, abbreviated month)
- **AND** format uses day as 2-digit, month as short name, year as 4-digit

#### Scenario: Missing Date Handling
- **GIVEN** a template with no `updated_at` field
- **WHEN** system formats date
- **THEN** system uses `created_at` as fallback
- **AND** if both missing, displays empty string (no crash)

### Requirement: Fallback Template Display
The dashboard MUST show static fallback templates when API fails or returns empty.

#### Scenario: API Error Fallback
- **GIVEN** `/api/templates` returns 500 error
- **WHEN** dashboard renders
- **THEN** system displays 6 hardcoded static templates
- **AND** templates are fully functional (buttons work)
- **AND** no error message shown to user

#### Scenario: Empty API Response Fallback
- **GIVEN** `/api/templates` returns empty array
- **WHEN** dashboard renders
- **THEN** system displays 6 hardcoded static templates
- **AND** provides user with access to at least basic templates

## Notes

- This delta aligns with existing `dynamize-dashboard-data` change
- Templates section is one of last hardcoded sections being dynamized
- Static templates preserved as fallback for reliability
- No breaking changes - existing functionality maintained
- Future enhancement: User-specific template favorites, search, filtering
