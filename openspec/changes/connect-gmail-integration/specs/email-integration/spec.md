# Email Integration Spec

## ADDED Requirements

### Requirement: Gmail Connection Management
The system SHALL allow users to securely connect and disconnect their Gmail accounts via OAuth authentication.

#### Scenario: First-time Gmail connection
- **WHEN** user navigates to /email without Gmail connected
- **THEN** system displays consent screen with Gmail connection options
- **AND** shows consent checkboxes for OAuth and AI reading
- **AND** "Connect with Gmail" button is disabled until both consents checked

#### Scenario: Gmail OAuth connection
- **WHEN** user clicks "Connect with Gmail" after providing consent
- **THEN** system redirects to Google OAuth authorize endpoint with Gmail scopes
- **AND** user approves permissions on Google consent screen
- **THEN** system receives OAuth callback with authorization code
- **AND** exchanges code for access token and refresh token
- **AND** stores refresh token securely in database
- **AND** redirects user to /email inbox view

#### Scenario: Gmail connection status check
- **WHEN** user with connected Gmail visits /email
- **THEN** system skips consent screen and shows inbox immediately
- **AND** displays last sync time in settings

#### Scenario: Gmail disconnection
- **WHEN** user clicks "Revoke Access" in email settings
- **THEN** system confirms action with warning dialog
- **AND** removes stored refresh token from database
- **AND** revokes token with Google OAuth API
- **AND** redirects to consent screen
- **AND** clears cached email data

### Requirement: Email List Retrieval
The system SHALL fetch and display emails from user's Gmail inbox using Gmail API.

#### Scenario: Initial email fetch
- **WHEN** user with connected Gmail views /email inbox
- **THEN** system calls Gmail API users.messages.list with INBOX label
- **AND** fetches metadata for up to 25 most recent messages
- **AND** extracts From, Subject headers and snippet
- **AND** maps to frontend email data structure
- **AND** displays emails in inbox list with proper formatting

#### Scenario: Email pagination
- **WHEN** user scrolls to bottom of email list
- **THEN** system fetches next page using pageToken from previous response
- **AND** appends new emails to existing list
- **AND** continues until no nextPageToken available

#### Scenario: Email refresh
- **WHEN** user clicks refresh button or auto-refresh timer triggers
- **THEN** system fetches latest emails from Gmail API
- **AND** merges new emails with existing cached data
- **AND** updates unread counts in folder tabs
- **AND** shows "Last synced: X minutes ago" timestamp

#### Scenario: Empty inbox
- **WHEN** Gmail API returns zero messages
- **THEN** system displays empty state with message "No emails found"
- **AND** shows explanation "Your inbox is empty or all emails are filtered"

#### Scenario: Gmail API rate limit
- **WHEN** Gmail API returns 429 Too Many Requests
- **THEN** system shows error message "Rate limit exceeded, try again in X minutes"
- **AND** implements exponential backoff (1s, 2s, 4s, 8s, 16s)
- **AND** caches last successful email list for display during cooldown

### Requirement: Email Display
The system SHALL display Gmail emails using existing email.vue UI components without visual changes.

#### Scenario: Email metadata display
- **WHEN** email is rendered in inbox list
- **THEN** system displays sender name and email address
- **AND** shows subject line with attachment icon if applicable
- **AND** displays snippet (first 140 characters of body)
- **AND** shows relative timestamp ("2h ago", "Yesterday", "Dec 15")
- **AND** indicates read/unread status with visual styling
- **AND** shows star icon if email is starred

#### Scenario: Email detail view
- **WHEN** user clicks email in list
- **THEN** system opens modal with full email content
- **AND** displays sender avatar with initials
- **AND** shows full sender email address
- **AND** displays formatted date and time
- **AND** renders email body (plain text or HTML)
- **AND** lists attachments with file names and sizes

#### Scenario: Email categorization
- **WHEN** email subject or content contains legal keywords
- **THEN** system assigns category type:
- "Contracts" for contract/vertrag keywords
- "Terminations" for termination/kündigung keywords
- "Reminders" for reminder/erinnerung keywords
- "General" for uncategorized emails
- **AND** displays category badge with color coding

### Requirement: Email Actions
The system SHALL allow users to perform common email actions via Gmail API.

#### Scenario: Star email
- **WHEN** user clicks star icon on email
- **THEN** system calls Gmail API modify endpoint
- **AND** adds STARRED label to message
- **AND** updates UI to show filled star icon
- **AND** increments starred folder count

#### Scenario: Unstar email
- **WHEN** user clicks filled star icon on starred email
- **THEN** system calls Gmail API modify endpoint
- **AND** removes STARRED label from message
- **AND** updates UI to show empty star icon
- **AND** decrements starred folder count

#### Scenario: Mark as read
- **WHEN** user opens email detail view
- **THEN** system calls Gmail API modify endpoint
- **AND** removes UNREAD label from message
- **AND** updates status from "Ungelesen" to "Read"
- **AND** decrements unread count in inbox tab

#### Scenario: Mark as unread
- **WHEN** user clicks "Mark as unread" button
- **THEN** system calls Gmail API modify endpoint
- **AND** adds UNREAD label to message
- **AND** updates status to "Ungelesen"
- **AND** increments unread count in inbox tab

### Requirement: Token Refresh Handling
The system SHALL transparently refresh Gmail access tokens when expired without user intervention.

#### Scenario: Expired access token
- **WHEN** cached Gmail access token expires (after 1 hour)
- **THEN** system automatically exchanges refresh token for new access token
- **AND** caches new access token with 15-minute TTL
- **AND** retries original Gmail API request
- **AND** returns results to user without error

#### Scenario: Invalid refresh token
- **WHEN** refresh token is revoked or expired
- **THEN** Gmail token refresh returns 401 Unauthorized
- **AND** system clears stored refresh token from database
- **AND** returns {error: 'not_linked'} to frontend
- **AND** frontend displays "Gmail connection lost, please reconnect"
- **AND** redirects user to consent screen

#### Scenario: Network timeout during refresh
- **WHEN** token refresh request times out
- **THEN** system retries refresh request up to 3 times
- **AND** if all retries fail, returns temporary error to frontend
- **AND** frontend shows "Unable to connect to Gmail, try again later"
- **AND** preserves stored refresh token for next attempt

### Requirement: Gmail Folder Navigation
The system SHALL support navigation between Gmail folders using label-based filtering.

#### Scenario: Inbox folder
- **WHEN** user selects Inbox tab
- **THEN** system fetches messages with labelIds=INBOX
- **AND** displays all emails not archived or deleted

#### Scenario: Starred folder
- **WHEN** user selects Starred tab
- **THEN** system filters locally cached emails with starred=true
- **AND** displays only starred messages
- **AND** shows count of starred emails

#### Scenario: Sent folder
- **WHEN** user selects Sent tab
- **THEN** system fetches messages with labelIds=SENT
- **AND** displays emails sent by user

#### Scenario: Archive folder
- **WHEN** user selects Archive tab
- **THEN** system fetches messages without INBOX label
- **AND** displays archived emails

### Requirement: Error Handling
The system SHALL handle Gmail API errors gracefully and provide clear user feedback.

#### Scenario: Network error
- **WHEN** Gmail API request fails due to network issue
- **THEN** system shows error message "Unable to connect to Gmail"
- **AND** provides "Retry" button
- **AND** logs error details for debugging

#### Scenario: Authentication error
- **WHEN** Gmail API returns 401 Unauthorized
- **THEN** system attempts token refresh
- **AND** if refresh fails, prompts re-authentication
- **AND** clears invalid tokens

#### Scenario: Malformed email data
- **WHEN** Gmail API returns email with missing fields
- **THEN** system provides default values:
- sender: "Unknown Sender"
- subject: "(no subject)"
- snippet: ""
- **AND** logs malformed data for investigation
- **AND** displays email without crashing UI
