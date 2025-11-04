## Why
- Google sign-in currently drops users on the email workspace, even when they only meant to reach the dashboard.
- Old Gmail-connection state in local storage makes the callback think it should finish a mailbox consent flow.
- Showing the email consent screen on every login confuses users and blocks the happy path.

## What Changes
- Track which OAuth flow (login vs Gmail connect) is running and clear Gmail return state when the flow is plain login.
- Ensure the callback always defaults to the dashboard unless the Gmail flow was explicitly requested and succeeded.
- Update frontend Gmail-connect helpers so only the consent workflow stores a return path and it is session-scoped.

## Impact
- Google logins from the landing modal land on `/dashboard` consistently.
- Users only see the email consent/connection UI when they explicitly connect Gmail from the email workspace.
- Gmail integration remains available without regressing existing backend security or scope handling.
