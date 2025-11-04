# Connect Assistant Page to Backend

## Why

The `/assistant` page currently exists in the frontend with a fully functional UI, but it's not properly integrated with the backend AI service. Users can see the interface but cannot have actual conversations with the AI assistant. The existing `/api/ai/complete` endpoint is available but not optimally configured for chat conversations, and chat messages are not being persisted to the database for conversation history.

**Problem**: Chat interface exists but doesn't connect to the trained Qwen legal model, no conversation persistence, and parameter mismatch between frontend and backend.

## What Changes

1. **Frontend API Integration** - Fix parameter mismatch in assistant.vue
   - Change `context_type` parameter to `context` to match backend expectations
   - Update error handling to show specific error messages
   - Add proper authentication token handling

2. **Backend Conversation Management** - Create dedicated chat endpoint
   - Add `/api/assistant/chat` endpoint specifically for conversational AI
   - Implement conversation history persistence to `assistant_messages` table
   - Support optional conversation_id for multi-turn conversations
   - Return conversation_id and message_id with responses

3. **Backend Enhancement** - Improve `/api/ai/complete` for chat use cases
   - Add conversation context support (last N messages)
   - Implement proper conversation history retrieval
   - Add rate limiting for chat endpoint (10 messages per minute per user)

4. **Database Interaction** - Add conversation management methods
   - Add `create_conversation_message` method to database.py
   - Add `get_conversation_history` method to database.py
   - Add `get_user_conversations` method to database.py

5. **Documentation** - Update project.md with chat endpoints
   - Document `/api/assistant/chat` endpoint
   - Document conversation_id management
   - Document rate limits and best practices

## Impact

**Affected Specs:**
- `specs/ai-assistant/spec.md` (will be created)
- `specs/authentication/spec.md` (existing - no changes, auth already works)

**Affected Code:**
- `/root/anwalts-frontend-new/pages/assistant.vue` - Update API call parameters
- `/root/backend-main.py` - Add `/api/assistant/chat` endpoint, enhance existing endpoint
- `/root/database.py` - Add conversation management methods
- `/root/openspec/project.md` - Add API documentation

**User Impact:**
- Users can now chat with the AI legal assistant on the `/assistant` page
- Conversations are persisted and can be retrieved later
- Multi-turn conversations with context awareness
- Rate limiting prevents abuse

**Breaking Changes:**
- None - this is a new feature addition
- Existing `/api/ai/complete` endpoint remains backward compatible

**Deployment Requirements:**
1. Backend container must be rebuilt and redeployed
2. Frontend container must be rebuilt and redeployed
3. No database migrations needed (assistant_messages table already exists)
4. No environment variable changes needed

**Testing Requirements:**
1. Test authentication flow on `/assistant` page
2. Test single-turn conversation (no conversation_id)
3. Test multi-turn conversation (with conversation_id)
4. Test rate limiting (>10 messages per minute)
5. Test conversation history retrieval
6. Verify messages saved to database
7. Test error handling (network failures, AI service failures)
8. Verify UI displays responses correctly
9. Test on live site https://portal-anwalts.ai/assistant
