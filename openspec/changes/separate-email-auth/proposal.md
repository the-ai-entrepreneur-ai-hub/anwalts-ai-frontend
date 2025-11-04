## Why
- Current Gmail integration implicitly binds to the signed-in portal account email, causing the email workspace to assume the login identity even when the user provides different Gmail credentials.
- Embedded Gmail refresh tokens live inside `user_profiles.data`, preventing multiple mailboxes per user and making consent revocation brittle.
- We need a clear separation between portal authentication and external email identities to avoid data leakage and regulatory risk.

## What Changes
- Introduce a first-class `email_accounts` data model linked to users but keyed by the external mailbox identity.
- Require explicit linking and selection of an email account before Gmail data is fetched; default to no account when none is connected.
- Update backend APIs, caches, and Nuxt server routes to read/write the new model instead of inferring from the login user record.
- Add migration scripts and data backfill to move existing Gmail state out of `user_profiles`.

## Impact
- Portal login flows remain unchanged, but email workspace loads will prompt for linking if no active mailbox is selected.
- Backend services will reference the new tables; existing tokens will be migrated.
- Data model documentation and ERDs must reflect the new entities so future work remains aligned.
