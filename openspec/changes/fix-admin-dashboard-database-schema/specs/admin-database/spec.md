## ADDED Requirements

### Requirement: Organization Settings Table Stores System Configuration
The system SHALL maintain an `organization_settings` table to persist organization-wide configuration.

#### Scenario: Organization settings table exists
- **GIVEN** the database is initialized
- **WHEN** admin queries organization settings
- **THEN** the `organization_settings` table exists with proper schema
- **AND** contains at least one row with default settings

#### Scenario: Default organization settings are seeded
- **GIVEN** fresh database initialization
- **WHEN** `organization_settings` table is created
- **THEN** a default row is inserted with sensible defaults
- **AND** includes language='de', timezone='Europe/Berlin', ai_model='qwen_legal_q4_k_m'

### Requirement: Analytics Events Table Tracks System Activity
The system SHALL maintain an `analytics_events` table to track system activity for admin dashboard.

#### Scenario: Analytics events table exists
- **GIVEN** the database is initialized
- **WHEN** admin queries recent activity
- **THEN** the `analytics_events` table exists with proper schema
- **AND** supports event_type, user_id, created_at columns

#### Scenario: Analytics events can be queried by date range
- **GIVEN** analytics_events table contains data
- **WHEN** admin requests events from last 7 days
- **THEN** query completes successfully with proper indexing
- **AND** results are grouped by event_type with counts

### Requirement: API Tokens Table Manages API Access Keys
The system SHALL maintain an `api_tokens` table to manage API access tokens.

#### Scenario: API tokens table exists
- **GIVEN** the database is initialized
- **WHEN** system queries active API tokens
- **THEN** the `api_tokens` table exists with proper schema
- **AND** supports token tracking with revoked_at column

#### Scenario: Active tokens can be counted
- **GIVEN** api_tokens table contains data
- **WHEN** admin dashboard queries active token count
- **THEN** query returns count of tokens where revoked_at IS NULL

### Requirement: Webhooks Table Manages Outbound Webhooks
The system SHALL maintain a `webhooks` table to manage webhook configurations.

#### Scenario: Webhooks table exists
- **GIVEN** the database is initialized
- **WHEN** system queries active webhooks
- **THEN** the `webhooks` table exists with proper schema
- **AND** supports webhook tracking with is_active column

#### Scenario: Active webhooks can be counted
- **GIVEN** webhooks table contains data
- **WHEN** admin dashboard queries active webhook count
- **THEN** query returns count of webhooks where is_active = true

### Requirement: Database Migration Creates All Required Tables
The system SHALL provide a migration script that creates all admin-related tables atomically.

#### Scenario: Migration script creates all tables
- **GIVEN** empty database without admin tables
- **WHEN** migration script is executed
- **THEN** all four tables are created successfully
- **AND** default data is inserted
- **AND** indexes are created for performance

#### Scenario: Migration is idempotent
- **GIVEN** migration script
- **WHEN** executed multiple times
- **THEN** does not fail on existing tables
- **AND** does not duplicate data
