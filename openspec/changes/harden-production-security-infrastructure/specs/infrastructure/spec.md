# Infrastructure Capability Specification Delta

## ADDED Requirements

### Requirement: Database Connection Pool Sizing
The system SHALL configure database connection pools to handle expected concurrent load without exhaustion.

#### Scenario: Production connection pool configuration
- **GIVEN** the backend application is being deployed to production
- **WHEN** the database connection pool is initialized
- **THEN** max_size MUST be at least 50 connections to support 50+ concurrent users
- **AND** min_size MUST be at least 10 connections for quick availability
- **AND** command_timeout MUST be 30 seconds or less to prevent long-running query blocking

#### Scenario: Connection pool under load
- **GIVEN** the system is handling 50 concurrent users
- **WHEN** database connections are requested
- **THEN** connections MUST be available without timeout errors
- **AND** no requests SHOULD fail due to connection pool exhaustion

#### Scenario: Connection recycling
- **GIVEN** database connections are in use over time
- **WHEN** connections reach max_queries threshold (50,000 queries)
- **THEN** connections MUST be recycled to prevent resource leaks
- **AND** inactive connections MUST be closed after max_inactive_connection_lifetime (300 seconds)

#### Scenario: Connection pool monitoring
- **GIVEN** the application is running in production
- **WHEN** monitoring metrics are collected
- **THEN** connection pool usage percentage MUST be tracked
- **AND** alerts MUST fire when pool usage exceeds 80%

### Requirement: Email Service Availability
The system SHALL ensure email delivery services are running and accessible for critical user communications.

#### Scenario: Mailhog container operational
- **GIVEN** the application stack is deployed
- **WHEN** containers are started
- **THEN** mailhog container MUST be running and healthy
- **AND** SMTP port 1025 MUST be accessible from backend container
- **AND** mailhog web UI MUST be accessible on port 8025

#### Scenario: SMTP connectivity verification
- **GIVEN** the backend service starts
- **WHEN** health checks are performed
- **THEN** SMTP connectivity to mailhog MUST be verified
- **AND** health check endpoint MUST report email service status

#### Scenario: Password reset email delivery
- **GIVEN** a user requests a password reset
- **WHEN** the password reset email is sent
- **THEN** the email MUST be delivered to mailhog
- **AND** the email MUST contain a valid reset token
- **AND** the email MUST be visible in mailhog web UI

### Requirement: AI Service Configuration and Fallback
The system SHALL properly configure AI services with graceful degradation when primary service unavailable.

#### Scenario: Together AI configuration
- **GIVEN** Together AI is selected as the AI provider
- **WHEN** AI_PROVIDER is set to "together"
- **THEN** TOGETHER_API_KEY MUST be configured with a valid API key
- **AND** the AI service MUST NOT log errors about missing API key

#### Scenario: Sidecar AI fallback
- **GIVEN** Together AI is configured but unavailable
- **WHEN** an AI completion is requested
- **THEN** the system MUST fall back to the local sidecar model
- **AND** a warning MUST be logged about Together AI unavailability
- **AND** the user request MUST NOT fail

#### Scenario: AI provider explicit configuration
- **GIVEN** no Together API key is available
- **WHEN** the system is deployed
- **THEN** AI_PROVIDER MUST be explicitly set to "sidecar"
- **AND** the AI service MUST use the local model without attempting Together API

#### Scenario: AI health check reporting
- **GIVEN** the AI service is initialized
- **WHEN** health checks are performed
- **THEN** AI service availability MUST be reported
- **AND** health check MUST indicate which provider is active (together or sidecar)
- **AND** health check MUST NOT fail due to Together API unavailability if sidecar is working

### Requirement: Redis Password Authentication
The system SHALL enforce authentication for Redis cache connections.

#### Scenario: Redis server authentication requirement
- **GIVEN** Redis container is being started
- **WHEN** Redis server is configured
- **THEN** Redis MUST be started with --requirepass flag
- **AND** Redis MUST reject unauthenticated connections

#### Scenario: Backend Redis authentication
- **GIVEN** the backend service connects to Redis
- **WHEN** the Redis connection is established
- **THEN** the connection string MUST include the Redis password
- **AND** authenticated operations MUST succeed

#### Scenario: Redis authentication failure handling
- **GIVEN** Redis requires authentication
- **WHEN** an unauthenticated connection is attempted
- **THEN** the connection MUST be rejected
- **AND** an authentication error MUST be logged

### Requirement: Service Health Monitoring
The system SHALL provide comprehensive health check endpoints for all critical services.

#### Scenario: Composite health check
- **GIVEN** the backend service is running
- **WHEN** the /health endpoint is called
- **THEN** health status MUST include database connectivity
- **AND** health status MUST include Redis connectivity
- **AND** health status MUST include AI service status
- **AND** health status MUST include SMTP connectivity

#### Scenario: Individual service failure reporting
- **GIVEN** a health check is performed
- **WHEN** any individual service is unhealthy
- **THEN** the overall health check MUST report "degraded" status
- **AND** the failing service MUST be identified in the response
- **AND** HTTP status MUST be 503 Service Unavailable

#### Scenario: All services healthy
- **GIVEN** a health check is performed
- **WHEN** all services are operational
- **THEN** the overall health check MUST report "healthy" status
- **AND** HTTP status MUST be 200 OK
