# Gmail Integration Proposal

## Why

The email section currently displays mock/template data and is not connected to real user Gmail accounts. Users cannot view, process, or manage their actual legal emails through the portal, which limits the platform's utility for real-world legal workflow management.

The Gmail API has been enabled on the existing Google OAuth credentials, and frontend email API routes already exist but are not connected to the authentication flow. This proposal completes the integration to enable users to:
- Connect their Gmail account securely via OAuth
- View real emails with the existing UI
- Process emails with the AI legal assistant for summaries, categorization, and draft responses

## What Changes

- **OAuth Flow Enhancement**: Add Gmail API scopes (`https://www.googleapis.com/auth/gmail.readonly`, `https://www.googleapis.com/auth/gmail.modify`) to Google OAuth flow
- **Token Storage**: Store and manage Gmail refresh tokens for persistent API access
- **Frontend Integration**: Connect email.vue consent screen to OAuth flow and replace mock data with real Gmail API calls
- **Email Processing**: Create backend endpoints to process emails with the legal-rag-api AI model for:
  - Email summarization
  - Priority/type categorization
  - Draft response generation
- **User Experience**: Maintain existing email UI while transitioning from template data to live Gmail data

## Impact

**Affected Specs:**
- `oauth-flow` (MODIFIED) - Add Gmail scopes and refresh token storage
- `email-integration` (ADDED) - New capability for Gmail API integration
- `ai-email-processing` (ADDED) - New capability for AI-powered email processing

**Affected Code:**
- Backend: `/root/backend-main.py` (OAuth flow, token storage)
- Backend: `/root/database.py` (Gmail token persistence)
- Frontend: `/root/anwalts-frontend-new/pages/email.vue` (OAuth connection, API integration)
- Frontend: `/root/anwalts-frontend-new/server/api/email/*.ts` (already exist, minor updates)

**Dependencies:**
- Gmail API enabled in Google Cloud Console (already configured)
- Google OAuth credentials configured (already configured)
- legal-rag-api container running (already deployed)

**Risk Level:** Medium
- OAuth scope changes require user re-consent
- Gmail API rate limits must be handled
- Refresh token security is critical
- No breaking changes to existing authentication

**Testing Requirements:**
- OAuth flow with Gmail scopes
- Email fetching and display
- AI processing accuracy
- Rate limiting and error handling
- Token refresh mechanism
