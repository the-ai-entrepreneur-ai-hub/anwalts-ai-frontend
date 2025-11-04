## Why
- Google sign-in currently requests Gmail modify scopes every time, forcing users through an unnecessary consent screen.
- This breaks the expected login journey and confuses users who only want to access the core product.

## What Changes
- Split Google OAuth scopes by flow so basic login uses only `openid email profile` while Gmail connections add mailbox scopes.
- Forward query parameters through OAuth proxy endpoints to let the frontend opt into Gmail mode explicitly.
- Set sensible defaults (`prompt=select_account`, `access_type=online`) for login while keeping Gmail flows on `prompt=consent` + offline access.

## Impact
- Users signing in with Google land on the dashboard without being prompted for Gmail access.
- Email workspace can still trigger full Gmail consent when the user explicitly connects their mailbox.
- Minimal regression risk; requires coordinated frontend + backend change plus container redeploy.
