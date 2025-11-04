# OAuth Flow Spec Delta

## MODIFIED Requirements

### Requirement: Google OAuth Scopes
The system SHALL request appropriate OAuth scopes during Google authentication based on user consent, including profile access and optional Gmail API access for email integration.

#### Scenario: Profile-only authentication
- **WHEN** user authenticates for basic profile access
- **THEN** system requests "openid email profile" scopes
- **AND** user can access profile and dashboard features

#### Scenario: Gmail integration authentication
- **WHEN** user connects Gmail from email section
- **THEN** system requests "openid email profile https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.modify" scopes
- **AND** OAuth authorization includes access_type=offline and prompt=consent
- **AND** user sees explicit permission request for Gmail access

#### Scenario: Gmail modify scope usage
- **WHEN** user modifies email labels (star, read/unread, archive)
- **THEN** system uses gmail.modify scope
- **AND** user can update email metadata without send permission

### Requirement: OAuth Token Storage
The system SHALL securely store OAuth refresh tokens per user for persistent API access to connected services.

#### Scenario: Gmail refresh token storage
- **WHEN** Google OAuth callback returns refresh token
- **THEN** system encrypts refresh token using Fernet encryption
- **AND** stores encrypted token in user_profiles.data['gmail_refresh_token']
- **AND** records consent timestamp in user_profiles.data['gmail_consent_timestamp']
- **AND** sets user_profiles.data['gmail_connected'] = True

#### Scenario: Refresh token retrieval
- **WHEN** backend needs to access Gmail API for user
- **THEN** system retrieves encrypted refresh token from database
- **AND** decrypts token using JWT_SECRET key
- **AND** uses token to obtain fresh access token

#### Scenario: Token revocation
- **WHEN** user revokes Gmail access from settings
- **THEN** system removes gmail_refresh_token from user_profiles.data
- **AND** sets gmail_connected = False
- **AND** revokes token with Google API
- **AND** user must re-authenticate to reconnect Gmail

### Requirement: OAuth Redirect URI Configuration
The system SHALL support multiple OAuth redirect URIs for different authentication flows and maintain backward compatibility.

#### Scenario: Gmail OAuth callback
- **WHEN** Google redirects after Gmail scope approval
- **THEN** system accepts callbacks at all configured redirect URIs:
- https://portal-anwalts.ai/api/auth/oauth/google/callback
- https://portal-anwalts.ai/auth/google/callback
- https://portal-anwalts.ai/api/auth/google/callback
- https://portal-anwalts.ai/auth/callback
- **AND** validates state parameter for CSRF protection
- **AND** exchanges code for tokens using client_secret
