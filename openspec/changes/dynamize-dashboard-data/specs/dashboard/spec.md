# Dashboard Capability Delta Specification

This delta spec defines requirements for transforming the dashboard from hard-coded demo data to dynamic, user-specific data.

## ADDED Requirements

### Requirement: User-Specific Dashboard Data

The dashboard SHALL display data specific to the currently authenticated user, with all values retrieved from the database based on the user's ID.

#### Scenario: Admin user views dashboard
- **GIVEN** Angela (admin) is logged in
- **WHEN** she navigates to `/dashboard`
- **THEN** the dashboard displays Angela's personal stats, documents, deadlines, and activity
- **AND** no data from other users is visible
- **AND** the welcome message displays "Willkommen zur?ck, Angela"

#### Scenario: Regular user views dashboard
- **GIVEN** a regular user is logged in
- **WHEN** they navigate to `/dashboard`
- **THEN** the dashboard displays their personal stats, documents, deadlines, and activity
- **AND** they do not see other users' data
- **AND** the welcome message displays their name

#### Scenario: Different users see different data
- **GIVEN** User A has 5 documents and User B has 12 documents
- **WHEN** User A views the dashboard
- **THEN** the documents count shows 5
- **WHEN** User B views the dashboard
- **THEN** the documents count shows 12

### Requirement: No Hard-Coded Values

The dashboard SHALL NOT contain any hard-coded numeric values, dates, names, or placeholder text that does not reflect actual data from the database.

#### Scenario: Stats cards display database values
- **GIVEN** a user has 7 cases, 23 documents, and 89 emails in the database
- **WHEN** they view the dashboard
- **THEN** the stats cards display "7", "23", and "89" respectively
- **AND** no hard-coded values like "42", "156", or "389" are displayed

#### Scenario: Documents list displays real documents
- **GIVEN** a user has documents titled "Mietvertrag" and "Arbeitsvertrag"
- **WHEN** they view the dashboard
- **THEN** the documents section displays "Mietvertrag" and "Arbeitsvertrag"
- **AND** does NOT display hard-coded names like "Klageentwurf Schmidt" or "NDA?Vorlage Kronos"

#### Scenario: Dates are calculated relative to current date
- **GIVEN** today is 2025-11-02
- **AND** a user has a deadline on 2025-11-03
- **WHEN** they view the dashboard
- **THEN** the deadline is labeled "Morgen" (tomorrow)
- **AND** NOT a hard-coded date like "28. Aug"

### Requirement: Personalized Welcome Message

The dashboard welcome message SHALL display the user's actual name retrieved from the authentication system.

#### Scenario: User with full name sees personalized greeting
- **GIVEN** a user named "Max M?ller" is logged in
- **WHEN** they view the dashboard
- **THEN** the welcome message displays "Willkommen zur?ck, Max M?ller"

#### Scenario: User without name sees email-based greeting
- **GIVEN** a user with email "user@example.com" but no name is logged in
- **WHEN** they view the dashboard
- **THEN** the welcome message displays "Willkommen zur?ck, user@example.com"

#### Scenario: Fallback for missing user data
- **GIVEN** user data cannot be loaded
- **WHEN** the dashboard renders
- **THEN** the welcome message displays "Willkommen zur?ck" (generic)
- **AND** no error is thrown

### Requirement: Real-Time Date Calculations

All dates and times on the dashboard SHALL be calculated relative to the current date/time, not hard-coded to specific dates.

#### Scenario: Relative time for recent documents
- **GIVEN** a document was updated 2 hours ago
- **WHEN** a user views the dashboard
- **THEN** the document shows "vor 2 Stunden"
- **AND** the time updates correctly if the page is reloaded later

#### Scenario: Relative deadline labels
- **GIVEN** a deadline is due today
- **WHEN** a user views the dashboard
- **THEN** the deadline is labeled "Heute"
- **GIVEN** a deadline is due tomorrow
- **THEN** the deadline is labeled "Morgen"
- **GIVEN** a deadline is due in 5 days
- **THEN** the deadline is labeled "in 5 Tagen"

#### Scenario: No hard-coded dates in JavaScript
- **GIVEN** the dashboard source code
- **WHEN** reviewed for hard-coded dates
- **THEN** there are NO date strings like "2025-08-21" or "2025-08-28"
- **AND** all dates use `new Date()` or are fetched from the API

### Requirement: Dashboard API Endpoint

The system SHALL provide a comprehensive API endpoint `/api/dashboard/summary` that returns all necessary dashboard data for the authenticated user.

#### Scenario: API returns complete dashboard data
- **GIVEN** a user is authenticated
- **WHEN** the frontend calls `GET /api/dashboard/summary`
- **THEN** the API returns a JSON response with:
  - `stats`: object with `newCases`, `documents`, `emails`, `nextDeadline`
  - `recentDocuments`: array of up to 3 recent documents
  - `upcomingDeadlines`: array of up to 3 upcoming deadlines
  - `recentActivity`: array of up to 3 recent activities
  - `continueSuggestion`: object or null for "continue working on" suggestion
  - `user`: object with `name` and `email`
  - `warnings`: array of warning messages (empty if no issues)

#### Scenario: API requires authentication
- **GIVEN** a user is not authenticated
- **WHEN** they call `GET /api/dashboard/summary`
- **THEN** the API returns 401 Unauthorized
- **AND** no user data is leaked

#### Scenario: API handles missing data gracefully
- **GIVEN** a new user with no documents, cases, or deadlines
- **WHEN** they call `GET /api/dashboard/summary`
- **THEN** the API returns:
  - `stats.newCases: 0`
  - `stats.documents: 0`
  - `stats.emails: 0`
  - `recentDocuments: []` (empty array)
  - `upcomingDeadlines: []` (empty array)
  - `recentActivity: []` (empty array)
- **AND** no errors are thrown

### Requirement: Empty State Handling

When a user has no data (e.g., new user), the dashboard SHALL display helpful empty states with clear calls to action, not error messages or blank sections.

#### Scenario: New user with no documents
- **GIVEN** a user has 0 documents
- **WHEN** they view the dashboard
- **THEN** the documents section displays "Noch keine Dokumente"
- **AND** a button "Neues Dokument" is shown
- **AND** no error message is displayed

#### Scenario: User with no upcoming deadlines
- **GIVEN** a user has 0 deadlines
- **WHEN** they view the dashboard
- **THEN** the deadlines section displays an appropriate empty state
- **AND** no error or "loading failed" message is shown

#### Scenario: Dashboard with all zeros is valid
- **GIVEN** a new user with 0 cases, 0 documents, 0 emails, 0 deadlines
- **WHEN** they view the dashboard
- **THEN** all stats cards show "0"
- **AND** all list sections show empty states
- **AND** the dashboard does NOT display error messages
- **AND** the UI remains fully functional (buttons work, navigation works)

### Requirement: Loading State Management

The dashboard SHALL display loading skeletons while data is being fetched, and transition smoothly to the loaded state once data arrives.

#### Scenario: Loading skeletons shown during fetch
- **GIVEN** a user navigates to `/dashboard`
- **WHEN** the API request is in progress
- **THEN** loading skeletons are displayed in stats cards, documents, and activity sections
- **AND** the page does not appear blank or broken

#### Scenario: Smooth transition to loaded state
- **GIVEN** loading skeletons are displayed
- **WHEN** the API returns data
- **THEN** the skeletons fade out and real data fades in
- **AND** the transition is smooth (no flashing or layout shift)

#### Scenario: Loading state timeout
- **GIVEN** the API request takes >10 seconds
- **WHEN** the timeout is reached
- **THEN** an error message is displayed
- **AND** a "Retry" button is provided

### Requirement: Error Handling

If the dashboard API fails to load data, the system SHALL display a user-friendly error message and provide a retry option, without breaking the entire page.

#### Scenario: Partial data failure
- **GIVEN** the documents query succeeds but the deadlines query fails
- **WHEN** the dashboard renders
- **THEN** the documents section displays correctly
- **AND** the deadlines section shows "Fristen konnten nicht geladen werden"
- **AND** a "Erneut versuchen" (Retry) button is provided
- **AND** the rest of the dashboard remains functional

#### Scenario: Complete API failure
- **GIVEN** the entire `/api/dashboard/summary` request fails (500 error)
- **WHEN** the dashboard renders
- **THEN** an error message "Dashboard konnte nicht geladen werden" is displayed
- **AND** a "Erneut versuchen" (Retry) button is provided
- **AND** clicking Retry re-fetches the data

#### Scenario: Network timeout
- **GIVEN** the API request times out (no response in 30 seconds)
- **WHEN** the timeout occurs
- **THEN** the dashboard displays "Zeit?berschreitung - Bitte ?berpr?fen Sie Ihre Internetverbindung"
- **AND** a "Erneut versuchen" button is provided

### Requirement: Performance Standards

The dashboard SHALL load and display data within 2 seconds of page load under normal conditions (database operational, network stable).

#### Scenario: Dashboard loads in acceptable time
- **GIVEN** a user with typical data volume (50 documents, 10 deadlines, 100 activities)
- **WHEN** they navigate to `/dashboard`
- **THEN** the page transitions from loading skeletons to data within 2 seconds
- **AND** all sections render without delay

#### Scenario: Database queries are optimized
- **GIVEN** the dashboard API queries
- **WHEN** executed against the database
- **THEN** each individual query completes in <50ms
- **AND** the total query time (all queries combined) is <200ms
- **AND** queries use appropriate indexes on `user_id` columns

#### Scenario: Limited result sets prevent slowdown
- **GIVEN** a user with 1000+ documents
- **WHEN** they view the dashboard
- **THEN** only the 3 most recent documents are fetched (LIMIT 3)
- **AND** the page loads as fast as for users with 5 documents
- **AND** no full table scans occur

### Requirement: Data Consistency

All dashboard data SHALL be fetched in a single API request to ensure consistency (e.g., stats match the lists shown, dates are synchronized).

#### Scenario: Stats match displayed lists
- **GIVEN** a user has exactly 3 documents
- **WHEN** they view the dashboard
- **THEN** the stats card shows "3" documents
- **AND** the documents list displays exactly 3 documents
- **AND** the count does not mismatch due to race conditions

#### Scenario: Single API call prevents staleness
- **GIVEN** the dashboard fetches data
- **WHEN** `/api/dashboard/summary` is called once
- **THEN** all sections (stats, documents, deadlines, activity) are populated from that single response
- **AND** no additional API calls are made for separate sections
- **AND** data is guaranteed to be from the same point in time

### Requirement: Database Schema Support

The system SHALL have database tables (`cases`, `deadlines`, `activities`) with proper schema and indexes to support dashboard queries.

#### Scenario: Cases table exists with user_id
- **GIVEN** the database is migrated
- **WHEN** the dashboard queries for cases
- **THEN** the `cases` table exists with columns: `id`, `user_id`, `title`, `status`, `created_at`
- **AND** an index on `user_id` enables fast queries

#### Scenario: Deadlines table supports date queries
- **GIVEN** the database is migrated
- **WHEN** the dashboard queries for upcoming deadlines
- **THEN** the `deadlines` table exists with columns: `id`, `user_id`, `title`, `due_date`, `priority`
- **AND** an index on `(user_id, due_date)` enables efficient sorting

#### Scenario: Activities table logs user events
- **GIVEN** the database is migrated
- **WHEN** the dashboard queries for recent activity
- **THEN** the `activities` table exists with columns: `id`, `user_id`, `activity_type`, `title`, `created_at`
- **AND** an index on `(user_id, created_at DESC)` enables fast recent activity queries

#### Scenario: Documents table has user_id and progress
- **GIVEN** the database is migrated
- **WHEN** the dashboard queries for recent documents
- **THEN** the `documents` table has columns: `user_id`, `progress` (0-100), `status`
- **AND** queries filter by `user_id` efficiently

## MODIFIED Requirements

*(None - this is a new capability being added)*

## REMOVED Requirements

*(None - no existing functionality is being removed)*

## RENAMED Requirements

*(None)*
