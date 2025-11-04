# Security Capability Specification Delta

## ADDED Requirements

### Requirement: Cryptographic Secret Management
The system SHALL use cryptographically secure random values for all authentication and encryption secrets in production environments.

#### Scenario: JWT secret generation
- **GIVEN** the system is being deployed to production
- **WHEN** the JWT secret is configured
- **THEN** the JWT_SECRET_KEY MUST be at least 64 bytes of cryptographically secure random data
- **AND** the JWT_SECRET_KEY MUST NOT be a development default value

#### Scenario: Database credential security
- **GIVEN** the database is being configured
- **WHEN** the database password is set
- **THEN** the POSTGRES_PASSWORD MUST be at least 32 bytes of cryptographically secure random data
- **AND** the POSTGRES_PASSWORD MUST NOT be a default or predictable value

#### Scenario: Cache credential security
- **GIVEN** Redis is being configured for production
- **WHEN** Redis authentication is enabled
- **THEN** the REDIS_PASSWORD MUST be at least 32 bytes of cryptographically secure random data
- **AND** Redis MUST require authentication via --requirepass flag

#### Scenario: Secret rotation invalidates sessions
- **GIVEN** the JWT secret is rotated
- **WHEN** users attempt to use existing tokens
- **THEN** all existing JWT tokens MUST be invalidated
- **AND** users MUST be required to re-authenticate

### Requirement: Network Port Security
The system SHALL NOT expose internal services (database, cache) to the public internet.

#### Scenario: Database port binding
- **GIVEN** PostgreSQL is running in a container
- **WHEN** the database port is configured
- **THEN** PostgreSQL port 5432 MUST be bound to 127.0.0.1 only
- **AND** PostgreSQL MUST NOT be accessible from public internet

#### Scenario: Cache port binding
- **GIVEN** Redis is running in a container
- **WHEN** the Redis port is configured
- **THEN** Redis port 6379 MUST be bound to 127.0.0.1 only
- **AND** Redis MUST NOT be accessible from public internet

#### Scenario: External port scan verification
- **GIVEN** the system is deployed to production
- **WHEN** an external port scan is performed on the public IP
- **THEN** only ports 80 (HTTP) and 443 (HTTPS) SHOULD be open
- **AND** ports 5432 (PostgreSQL) and 6379 (Redis) MUST NOT respond

#### Scenario: Firewall rule enforcement
- **GIVEN** network security is being hardened
- **WHEN** firewall rules are configured
- **THEN** inbound connections to port 5432 MUST be denied from non-localhost sources
- **AND** inbound connections to port 6379 MUST be denied from non-localhost sources

### Requirement: OAuth Client Secret Protection
The system SHALL protect OAuth client secrets and ensure they are only accessible to backend services.

#### Scenario: Frontend environment isolation
- **GIVEN** the frontend container is being configured
- **WHEN** environment variables are set
- **THEN** GOOGLE_CLIENT_SECRET MUST NOT be present in frontend environment
- **AND** GOOGLE_CLIENT_SECRET MUST only be accessible to backend services

#### Scenario: OAuth secret usage validation
- **GIVEN** an OAuth flow is initiated
- **WHEN** the OAuth provider requires the client secret
- **THEN** the backend MUST retrieve the secret from secure environment variables
- **AND** the frontend MUST NOT have access to the client secret

### Requirement: Configuration Backup Before Changes
The system SHALL maintain backups of configuration files before security-critical changes.

#### Scenario: Pre-deployment configuration backup
- **GIVEN** security-critical configuration changes are about to be applied
- **WHEN** the deployment process begins
- **THEN** current .env file MUST be backed up with timestamp
- **AND** current docker-compose.yml MUST be backed up with timestamp
- **AND** backup files MUST be stored in /root with .backup.YYYYMMDD_HHMMSS extension

#### Scenario: Rollback capability verification
- **GIVEN** a security change has been deployed
- **WHEN** issues are discovered requiring rollback
- **THEN** the system MUST be able to restore from backup configurations
- **AND** rollback MUST restore previous secret values
- **AND** rollback procedure MUST be documented

### Requirement: Secret Documentation and Storage
The system SHALL maintain secure documentation of all production secrets.

#### Scenario: Secret vault storage
- **GIVEN** new secrets are generated for production
- **WHEN** secrets are created
- **THEN** secrets MUST be stored in a secure vault (1Password, LastPass, or equivalent)
- **AND** secrets MUST include metadata (service, purpose, rotation date)

#### Scenario: Secret rotation tracking
- **GIVEN** a secret is rotated
- **WHEN** the new secret is deployed
- **THEN** the rotation date MUST be recorded
- **AND** the old secret MUST be marked as deprecated
- **AND** a reminder for next rotation MUST be set (90 days recommended)
