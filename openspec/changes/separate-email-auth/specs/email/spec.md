## ADDED Requirements

### Requirement: Email Accounts Are Explicitly Linked
Portal users MUST link an external mailbox before the email workspace can read or mutate messages.

#### Scenario: No linked account blocks email fetch
- **GIVEN** a signed-in portal user without an active email account
- **WHEN** they open the email workspace
- **THEN** the backend responds with `401 Email account not connected`
- **AND** the UI prompts the user to connect an email account.

#### Scenario: Linking stores account independently of login email
- **GIVEN** a portal user whose login email is `caseworker@kanzlei.de`
- **WHEN** they complete Gmail OAuth for `assistant.inbox@gmail.com`
- **THEN** the system persists `assistant.inbox@gmail.com` as a distinct email account record
- **AND** subsequent email fetches use this external identity instead of the login email.

### Requirement: Multi-Account Support
Users MUST be able to store multiple external mailboxes and choose which one is active.

#### Scenario: Switching active email account
- **GIVEN** a user who linked `court.updates@gmail.com` and `assistant.inbox@gmail.com`
- **WHEN** they select `court.updates@gmail.com` in the email workspace
- **THEN** subsequent email API calls use the selected account's OAuth tokens.

### Requirement: Tokens Stored Outside User Profile Blob
Gmail OAuth artifacts MUST be persisted in a dedicated table keyed by the email account.

#### Scenario: Refresh token moved out of user_profiles
- **GIVEN** a migrated installation
- **WHEN** the migration runs
- **THEN** any `gmail_refresh_token` previously embedded in `user_profiles.data` is moved into the `email_accounts` storage
- **AND** the user profile JSON no longer contains Gmail token fields.

### Requirement: Logout Clears Active Email Context
Logging out MUST remove the active email account selection to prevent cross-user leakage.

#### Scenario: Logout removes active account cookie
- **GIVEN** a user with an active email account selected
- **WHEN** they log out of the portal
- **THEN** the system clears the cookie/session flag referencing the active email account.
