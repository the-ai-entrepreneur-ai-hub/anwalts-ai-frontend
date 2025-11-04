# Implementation Tasks

## 1. Backend - Database Layer
- [ ] 1.1 Add `create_conversation_message` method to database.py
  - Parameters: user_id, role, content, conversation_id (optional), model (optional)
  - Returns: message_id, conversation_id, created_at
  - Auto-generates conversation_id if not provided
- [ ] 1.2 Add `get_conversation_history` method to database.py
  - Parameters: conversation_id, limit (default 50)
  - Returns: List of messages ordered by created_at ASC
  - Include: id, role, content, model, created_at
- [ ] 1.3 Add `get_user_conversations` method to database.py (for future use)
  - Parameters: user_id, limit (default 20)
  - Returns: List of conversations with last message preview

## 2. Backend - API Endpoint
- [ ] 2.1 Create `/api/assistant/chat` POST endpoint in backend-main.py
  - Accept: message, conversation_id (optional), model (optional), max_tokens (optional), temperature (optional)
  - Require authentication via `get_current_user`
  - Validate message length (max 4000 characters)
- [ ] 2.2 Implement conversation history retrieval
  - If conversation_id provided, fetch last 5 messages
  - Build context string from conversation history
- [ ] 2.3 Call ai_service.generate_completion with context
  - Pass user message as prompt
  - Pass conversation history as context
  - Use default model: qwen_legal_q4_k_m
- [ ] 2.4 Save user message to database
  - Save before AI generation to track all user inputs
  - Generate new conversation_id if not provided
- [ ] 2.5 Save assistant response to database
  - Save after successful AI generation
  - Link to same conversation_id
- [ ] 2.6 Implement rate limiting
  - Use Redis to track message count per user per minute
  - Limit: 10 messages per minute
  - Return 429 status code if exceeded
- [ ] 2.7 Return response with conversation metadata
  - Return: content, conversation_id, message_id, model, usage, generation_time_ms

## 3. Backend - Error Handling
- [ ] 3.1 Handle AI service failures gracefully
  - Return user-friendly error message in German
  - Log detailed error for debugging
  - Still save user message even if AI fails
- [ ] 3.2 Handle database connection errors
  - Return 503 status code with retry message
- [ ] 3.3 Handle invalid conversation_id
  - Return 404 if conversation doesn't belong to user
  - Security: Prevent accessing other users' conversations

## 4. Frontend - API Integration
- [ ] 4.1 Update sendMessage function in assistant.vue
  - Change API endpoint to `/api/assistant/chat`
  - Change payload structure to match new endpoint
  - Remove `context_type` parameter (backend doesn't use it)
- [ ] 4.2 Add conversation_id state management
  - Add ref for currentConversationId
  - Store conversation_id from first response
  - Include in subsequent messages for same conversation
- [ ] 4.3 Update response handling
  - Extract content from response
  - Store conversation_id from response
  - Handle error responses properly
- [ ] 4.4 Improve error messages
  - Display specific error messages from backend
  - Show rate limit message when 429 received
  - Show retry option on failures
- [ ] 4.5 Update clearChat function
  - Reset currentConversationId when clearing chat
  - Confirm before clearing ongoing conversation

## 5. Frontend - Authentication
- [ ] 5.1 Add authentication token to API requests
  - Get token from localStorage.getItem('auth_token')
  - Add Authorization: Bearer {token} header
  - Handle 401 responses by redirecting to login
- [ ] 5.2 Test unauthenticated access
  - Verify redirect to login page if not authenticated
  - Verify proper error message display

## 6. Testing
- [ ] 6.1 Test single-turn conversation (new conversation)
  - Send first message without conversation_id
  - Verify response contains conversation_id
  - Verify messages saved to database
- [ ] 6.2 Test multi-turn conversation
  - Send second message with conversation_id from step 6.1
  - Verify context from previous message is used
  - Verify all messages linked to same conversation_id
- [ ] 6.3 Test authentication
  - Test with valid token
  - Test with expired token (should get 401)
  - Test with no token (should get 401)
- [ ] 6.4 Test rate limiting
  - Send 11 messages rapidly
  - Verify 11th message gets 429 status
  - Wait 1 minute and verify can send again
- [ ] 6.5 Test error handling
  - Test with invalid conversation_id
  - Test with message exceeding 4000 characters
  - Test with AI service unavailable (simulate)
- [ ] 6.6 Test UI behavior
  - Verify loading indicator shows during AI generation
  - Verify error messages display correctly
  - Verify messages display with proper formatting
  - Verify timestamps display correctly

## 7. Deployment
- [ ] 7.1 Rebuild backend Docker container
  - Run: docker build -f Dockerfile.backend -t anwalts-backend:latest .
- [ ] 7.2 Restart backend container
  - Run: docker-compose restart backend
  - Verify container is healthy
- [ ] 7.3 Rebuild frontend Docker container
  - Run: cd anwalts-frontend-new && docker build -t anwalts-frontend:latest .
- [ ] 7.4 Restart frontend container
  - Run: docker-compose restart frontend
  - Verify container is healthy
- [ ] 7.5 Verify deployment on live site
  - Visit https://portal-anwalts.ai/assistant
  - Login with test account
  - Send test message
  - Verify response received
  - Verify message saved in database

## 8. Documentation
- [ ] 8.1 Add endpoint documentation to openspec/project.md
  - Document `/api/assistant/chat` request/response format
  - Document rate limiting behavior
  - Document conversation_id management
- [ ] 8.2 Add usage examples
  - Show example single-turn request
  - Show example multi-turn request
  - Show example error responses

## 9. Validation
- [ ] 9.1 Check database for saved messages
  - Query assistant_messages table
  - Verify user_id, conversation_id, role, content populated
- [ ] 9.2 Verify Redis rate limiting
  - Check Redis keys for rate limit counters
  - Verify TTL is set correctly (60 seconds)
- [ ] 9.3 Test end-to-end on live site
  - Complete conversation with 3-4 messages
  - Verify all responses are contextually relevant
  - Verify no errors in browser console
  - Verify no errors in backend logs
