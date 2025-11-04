# Authentication Capability Specification Delta

## ADDED Requirements

### Requirement: Token Blacklist Memory Management
The system SHALL prevent memory exhaustion from unbounded token blacklist growth.

#### Scenario: Redis-based blacklist with TTL
- **GIVEN** a user logs out and their token is blacklisted
- **WHEN** the token is added to the blacklist
- **THEN** the token MUST be stored in Redis with a TTL equal to the token's remaining validity
- **AND** the token MUST automatically expire from the blacklist when it would naturally expire

#### Scenario: In-memory blacklist removal
- **GIVEN** the authentication service is refactored for production
- **WHEN** token blacklisting is implemented
- **THEN** in-memory Set storage MUST NOT be used for production blacklist
- **AND** Redis MUST be the sole source of truth for blacklisted tokens

#### Scenario: Blacklist cleanup scheduler
- **GIVEN** the backend service starts
- **WHEN** the startup event is triggered
- **THEN** a periodic cleanup task MUST be scheduled to run every hour
- **AND** the cleanup task MUST remove expired tokens from Redis

#### Scenario: Blacklist memory stability
- **GIVEN** the system has been running for 30 days
- **WHEN** memory usage is measured
- **THEN** blacklist memory usage MUST NOT grow unbounded
- **AND** blacklist size MUST correlate with active sessions, not all-time sessions

### Requirement: OAuth Callback Error Handling
The system SHALL handle OAuth callback errors gracefully without throwing TypeErrors.

#### Scenario: Missing Set-Cookie header handling
- **GIVEN** an OAuth callback is received from the backend
- **WHEN** the backend response does not include Set-Cookie headers (error case)
- **THEN** the frontend proxy MUST handle the missing header gracefully
- **AND** the frontend MUST NOT throw TypeError
- **AND** the redirect MUST proceed without attempting to set cookies

#### Scenario: Null cookie value handling
- **GIVEN** an OAuth callback is proxying cookies
- **WHEN** a cookie value is null or undefined
- **THEN** the cookie MUST NOT be appended to the response
- **AND** only valid string cookies MUST be forwarded

#### Scenario: OAuth error response propagation
- **GIVEN** the backend OAuth endpoint returns an error response
- **WHEN** the frontend proxy receives the error
- **THEN** the error MUST be properly propagated to the user
- **AND** any valid cookies MUST still be forwarded
- **AND** no TypeError MUST be thrown

#### Scenario: Cookie validation before forwarding
- **GIVEN** cookies are being forwarded from backend to frontend
- **WHEN** each cookie is processed
- **THEN** each cookie MUST be validated as a non-empty string
- **AND** only valid cookies MUST be appended to the response headers

### Requirement: Rate Limiting on Authentication Endpoints
The system SHALL prevent brute force attacks and abuse through rate limiting.

#### Scenario: Login endpoint rate limiting
- **GIVEN** a user attempts multiple login requests
- **WHEN** more than 5 login attempts are made within 1 minute from the same IP
- **THEN** subsequent requests MUST be rejected with HTTP 429 Too Many Requests
- **AND** a Retry-After header MUST indicate when requests can resume

#### Scenario: Registration endpoint rate limiting
- **GIVEN** registration requests are received from an IP address
- **WHEN** more than 3 registration attempts are made within 1 hour from the same IP
- **THEN** subsequent requests MUST be rejected with HTTP 429 Too Many Requests
- **AND** a Retry-After header MUST indicate when requests can resume

#### Scenario: Password reset rate limiting
- **GIVEN** password reset requests are received from an IP address
- **WHEN** more than 3 password reset attempts are made within 1 hour from the same IP
- **THEN** subsequent requests MUST be rejected with HTTP 429 Too Many Requests
- **AND** a Retry-After header MUST indicate when requests can resume

#### Scenario: OAuth callback rate limiting
- **GIVEN** OAuth callback requests are received from an IP address
- **WHEN** more than 10 callback attempts are made within 1 minute from the same IP
- **THEN** subsequent requests MUST be rejected with HTTP 429 Too Many Requests
- **AND** this prevents rapid callback replay attacks

#### Scenario: Rate limit state persistence
- **GIVEN** rate limiting is implemented
- **WHEN** rate limit counters are stored
- **THEN** counters MUST be stored in Redis for distributed state
- **AND** counters MUST automatically expire after the rate limit window

#### Scenario: Rate limit configuration
- **GIVEN** rate limits are being configured
- **WHEN** the backend service starts
- **THEN** rate limit values MUST be configurable via environment variables
- **AND** default values MUST provide reasonable protection

### Requirement: Distributed OAuth Callback Locking
The system SHALL prevent race conditions in OAuth callback processing that create duplicate users.

#### Scenario: OAuth callback lock acquisition
- **GIVEN** an OAuth callback request is received
- **WHEN** the callback handler begins processing
- **THEN** a distributed lock MUST be acquired on key "oauth:lock:{code}:{state}"
- **AND** the lock MUST have a 10-second timeout
- **AND** the lock MUST be released after processing

#### Scenario: Concurrent callback requests
- **GIVEN** multiple identical OAuth callback requests arrive simultaneously
- **WHEN** both requests attempt to process the same OAuth code and state
- **THEN** only one request MUST successfully acquire the lock
- **AND** the second request MUST wait for the lock or timeout
- **AND** no duplicate user accounts MUST be created

#### Scenario: OAuth completion check
- **GIVEN** an OAuth callback is being processed with lock held
- **WHEN** processing begins
- **THEN** the handler MUST check if the OAuth flow was already completed
- **AND** if already completed, the existing result MUST be returned
- **AND** duplicate processing MUST be prevented

#### Scenario: OAuth state uniqueness
- **GIVEN** OAuth state tokens are generated
- **WHEN** a new OAuth flow begins
- **THEN** the state token MUST be unique
- **AND** a database unique constraint MUST enforce state token uniqueness
- **AND** duplicate state tokens MUST be rejected

### Requirement: JWT Secret Rotation Impact
The system SHALL properly handle JWT secret rotation and its impact on existing sessions.

#### Scenario: Secret rotation invalidates all tokens
- **GIVEN** the JWT secret is rotated in production
- **WHEN** users attempt to authenticate with existing tokens
- **THEN** all tokens signed with the old secret MUST be rejected
- **AND** users MUST be required to log in again

#### Scenario: Token verification after rotation
- **GIVEN** the JWT secret has been rotated
- **WHEN** a token is verified
- **THEN** only tokens signed with the current secret MUST be valid
- **AND** tokens signed with previous secrets MUST fail verification

#### Scenario: User notification of rotation
- **GIVEN** the JWT secret rotation is complete
- **WHEN** the system returns to service
- **THEN** users MUST receive notification that sessions have expired
- **AND** the notification MUST instruct users to log in again
