# Update Email Provider Options

## Why

The email workspace still offers a "Login with Outlook" pathway that does not work in production. It confuses admins and test users because the button suggests a Microsoft OAuth integration that has never been wired up. At the same time, our legal customers primarily use firm-hosted mailboxes (Exchange/IMAP on their own domains), so they cannot connect through the existing Gmail-only flow. We need to remove the broken Outlook CTA and replace it with a guided path for domain-hosted mail that aligns with compliance expectations.

## What Changes

- **UI adjustments:** remove the Outlook login button from the email consent screen and all related prompts/tooltips.
- **Domain email connector:** introduce a new "Connect firm email" wizard that supports custom domain addresses (e.g. `name@kanzlei.de`) using service accounts or IMAP credentials, following the security pattern we use for Gmail (separate consent for mailbox reading and AI processing).
- **Backend capability:** add endpoints for storing encrypted domain-mail credentials (OAuth client secret or app password) and managing sync status separately from Gmail accounts.
- **Access policy:** enforce that only organization admins can add shared domain email connections, with per-user visibility controls.
- **Migration:** gracefully hide Outlook for existing users and surface guidance for moving any prior Outlook testers onto the new domain connector.

## Impact

**Affected specs:**
- `email-auth` (MODIFIED) ? remove Outlook provider requirement and clarify Gmail vs domain connectors.
- `email-auth` (ADDED) ? define new requirements for domain email connection management.

**Affected code:**
- Frontend: `pages/email.vue`, `components/EmailConsent*.vue`, `stores/email.ts`.
- Backend: `backend-main.py`, `database.py`, potential new IMAP connector module.
- Infrastructure: Secrets/config for domain SMTP/IMAP service accounts.

**Dependencies:**
- Secure credential storage (Postgres + encryption key, existing mechanism can likely be reused).
- IMAP/Exchange client library (e.g. `imapclient` or Microsoft Graph if OAuth is preferred).
- Admin UX updates for managing domain mailboxes.

**Risk level:** High ? introduces new authentication surface and needs careful security review.

**Testing requirements:**
- Consent screen renders without Outlook CTA.
- Domain connector happy path: add credentials, establish sync, view emails.
- Permission enforcement: only admins can add/remove domain connectors.
- Error handling for invalid credentials and connection failures.
- Regression on Gmail connector unaffected.
