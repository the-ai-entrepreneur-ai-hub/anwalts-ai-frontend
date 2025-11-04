## MODIFIED Requirements
### Requirement: Email Consent Screen Provider Options
The email workspace MUST only advertise connection methods that are fully supported in production.

#### Scenario: Outlook CTA Removed
- **WHEN** a user opens the email consent screen
- **THEN** no "Login with Outlook" button or copy is shown
- **AND** only the Gmail connector and the new firm-domain connector are presented.

#### Scenario: Legacy Deep Links Redirect
- **GIVEN** a user follows an old `/email?provider=outlook` link
- **WHEN** the page resolves provider options
- **THEN** the experience redirects back to the default consent screen
- **AND** displays current connection choices without breaking.

## ADDED Requirements
### Requirement: Firm Domain Email Connection
The system MUST allow organisation admins to link firm-hosted mailboxes (custom domains) with explicit consent for mailbox access and AI processing.

#### Scenario: Admin Connects Firm Mailbox
- **GIVEN** the signed-in user has an admin role
- **WHEN** they complete the "Connect firm email" wizard with a domain address
- **THEN** the backend stores the provided credentials encrypted and scoped to that organisation
- **AND** the mailbox appears in the email workspace with sync status indicators.

#### Scenario: Non-Admin Attempt Rejected
- **GIVEN** a non-admin user opens the firm email connector
- **WHEN** they attempt to submit credentials
- **THEN** the system blocks the action with "Administratorrechte erforderlich"
- **AND** no credentials are stored.

#### Scenario: Consent Mirrors Gmail Pattern
- **WHEN** an admin starts the firm email connector
- **THEN** the UI requires separate acknowledgement for mailbox access and AI processing
- **AND** the wizard cannot finish until both consents are accepted.

### Requirement: Domain Connector Error Handling
The system MUST surface actionable feedback when firm mail connection validation fails.

#### Scenario: Invalid Credentials
- **WHEN** the connector cannot authenticate with the provided domain mailbox
- **THEN** the workflow displays an error explaining the failure (e.g. "Benutzername oder App-Passwort ungültig")
- **AND** keeps the wizard open so the admin can retry without losing the entered address.

#### Scenario: Unsupported Domain Protocol
- **WHEN** the domain lacks IMAP/Graph support
- **THEN** the connector aborts the flow with guidance to contact support
- **AND** no partial records are left in the database.
