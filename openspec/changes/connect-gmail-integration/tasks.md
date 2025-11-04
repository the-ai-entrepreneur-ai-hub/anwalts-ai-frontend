# Implementation Tasks

## 1. Backend OAuth Enhancement
- [ ] 1.1 Update Google OAuth scopes in backend-main.py to include Gmail API access
- [ ] 1.2 Add refresh token extraction and storage in OAuth callback
- [ ] 1.3 Create database methods for storing/retrieving Gmail refresh tokens per user
- [ ] 1.4 Add endpoint to check Gmail connection status

## 2. Frontend OAuth Connection
- [ ] 2.1 Update email.vue consent screen to trigger backend OAuth flow with Gmail scopes
- [ ] 2.2 Handle OAuth callback and store connection state
- [ ] 2.3 Add error handling for OAuth failures
- [ ] 2.4 Update settings modal to show Gmail connection status

## 3. Email Fetching Integration
- [ ] 3.1 Replace mock email data in email.vue with API calls to /api/email/list
- [ ] 3.2 Implement pagination for large email lists
- [ ] 3.3 Add loading states during email fetch
- [ ] 3.4 Handle empty state when no emails exist
- [ ] 3.5 Implement email refresh functionality

## 4. Email Display Enhancement
- [ ] 4.1 Map Gmail API response fields to existing UI components
- [ ] 4.2 Handle email attachments from Gmail API
- [ ] 4.3 Implement star/unstar functionality via /api/email/modify
- [ ] 4.4 Implement mark as read/unread functionality
- [ ] 4.5 Add proper date formatting for real timestamps

## 5. AI Email Processing Backend
- [ ] 5.1 Create POST /api/email/process endpoint
- [ ] 5.2 Implement email content extraction from Gmail API
- [ ] 5.3 Connect to legal-rag-api for email summarization
- [ ] 5.4 Add email categorization logic (contract, termination, reminder, etc.)
- [ ] 5.5 Implement draft response generation
- [ ] 5.6 Store AI processing results in database
- [ ] 5.7 Add rate limiting for AI processing requests

## 6. Frontend AI Integration
- [ ] 6.1 Update email detail modal to display AI summaries
- [ ] 6.2 Add button to trigger AI processing for individual emails
- [ ] 6.3 Display AI-generated email categories and tags
- [ ] 6.4 Show draft responses with edit capability
- [ ] 6.5 Add loading states during AI processing

## 7. Error Handling & Edge Cases
- [ ] 7.1 Handle Gmail API rate limiting with exponential backoff
- [ ] 7.2 Handle expired refresh tokens with re-authentication flow
- [ ] 7.3 Add error messages for network failures
- [ ] 7.4 Handle malformed email data gracefully
- [ ] 7.5 Add logging for debugging OAuth and API issues

## 8. Security & Privacy
- [ ] 8.1 Encrypt Gmail refresh tokens in database
- [ ] 8.2 Add user consent tracking for AI email reading
- [ ] 8.3 Implement token revocation endpoint
- [ ] 8.4 Add audit logging for email access
- [ ] 8.5 Ensure HTTPS for all OAuth redirects

## 9. Testing & Validation
- [ ] 9.1 Test OAuth flow with Gmail scopes end-to-end
- [ ] 9.2 Test email fetching with various Gmail account states
- [ ] 9.3 Test AI processing with different email types
- [ ] 9.4 Test pagination with large email volumes
- [ ] 9.5 Test token refresh mechanism
- [ ] 9.6 Test error handling for API failures
- [ ] 9.7 Verify UI updates correctly with real data

## 10. Documentation & Deployment
- [ ] 10.1 Update openspec/project.md with Gmail API documentation
- [ ] 10.2 Document Gmail API rate limits and quotas
- [ ] 10.3 Build and deploy updated backend container
- [ ] 10.4 Build and deploy updated frontend container
- [ ] 10.5 Verify live site functionality at https://portal-anwalts.ai
