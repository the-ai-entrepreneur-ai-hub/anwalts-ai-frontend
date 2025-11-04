# Design Document: Assistant Chat Backend Integration

## Context

The Anwalts AI platform has a fully functional frontend chat interface at `/assistant` but lacks backend integration. The platform already has:
- A trained Qwen legal model accessible via ai_service.py
- An authentication system using JWT tokens
- A database schema with assistant_messages table
- An existing `/api/ai/complete` endpoint (generic AI completion)

**Goal**: Enable real-time conversational AI on the `/assistant` page with conversation persistence and context awareness.

**Stakeholders**: End users (lawyers), development team

**Constraints**:
- Must not break existing `/api/ai/complete` endpoint
- Must use existing authentication (JWT tokens)
- Must use existing database schema (no migrations)
- Must work with existing Qwen legal model via sidecar
- Must be deployed to live site without downtime

## Goals / Non-Goals

### Goals
1. Enable chat functionality on `/assistant` page
2. Persist all conversations to database
3. Support multi-turn conversations with context
4. Implement rate limiting to prevent abuse
5. Provide clear error messages in German
6. Maintain backward compatibility with existing endpoints

### Non-Goals
1. Building new AI models or retraining existing models
2. Implementing conversation search or filtering (future feature)
3. Implementing conversation sharing or export (future feature)
4. Real-time streaming responses (future enhancement)
5. Voice input/output (out of scope)
6. Multi-language support beyond German (future)

## Decisions

### Decision 1: Create New `/api/assistant/chat` Endpoint vs Modify Existing `/api/ai/complete`

**Chosen**: Create new `/api/assistant/chat` endpoint

**Rationale**:
- `/api/ai/complete` is generic and may be used by other features
- Chat-specific logic (conversation history, context management) doesn't belong in generic endpoint
- Clear separation of concerns
- Easier to add chat-specific features (typing indicators, streaming) later
- Existing endpoint remains stable for other use cases

**Alternatives Considered**:
1. Modify `/api/ai/complete` to handle conversations
   - Rejected: Would mix generic completion with conversation logic
   - Risk of breaking existing functionality
2. Create `/api/chat` without "assistant" prefix
   - Rejected: Less clear, could conflict with future chat features (user-to-user chat)

### Decision 2: Conversation History Context Management

**Chosen**: Include last 5 messages as context, formatted as "User: ... | Assistant: ..."

**Rationale**:
- Provides sufficient context for legal questions (most legal queries are 2-3 turns)
- Limits token usage and latency
- Simple implementation using existing database queries
- Easy to adjust limit in future if needed

**Alternatives Considered**:
1. Include all messages in conversation
   - Rejected: Could exceed token limits for long conversations
   - Performance impact (latency, cost)
2. Use semantic search to find relevant past messages
   - Rejected: Over-engineering for MVP
   - Adds complexity without proven benefit
3. No context (stateless conversations)
   - Rejected: Poor user experience for follow-up questions

### Decision 3: Rate Limiting Strategy

**Chosen**: 10 messages per minute per user, using Redis

**Rationale**:
- Prevents abuse and excessive API usage
- Redis already available in infrastructure
- Per-user limiting is fair (doesn't penalize all users for one abuser)
- 10 messages/minute is generous for legitimate use (most conversations are slower)
- Can be adjusted easily via environment variable in future

**Implementation**:
```python
# Redis key: rate:assistant_chat:{user_id}
# Value: message count
# TTL: 60 seconds
```

**Alternatives Considered**:
1. No rate limiting
   - Rejected: Risk of abuse, cost concerns
2. Global rate limiting (all users share limit)
   - Rejected: Unfair, one abuser impacts all users
3. Token-based rate limiting (track tokens not messages)
   - Rejected: More complex, harder for users to understand

### Decision 4: Error Handling Strategy

**Chosen**: Always save user message, return user-friendly errors in German

**Rationale**:
- User messages are valuable even if AI fails (can be reviewed later)
- German error messages match UI language and user expectations
- Specific error codes help debugging (429 for rate limit, 503 for service unavailable)
- Graceful degradation: user knows system received their message

**Error Categories**:
1. **Rate Limit (429)**: "Sie haben das Nachrichtenlimit überschritten. Bitte warten Sie einen Moment."
2. **AI Service Failure (503)**: "Ich konnte die Antwort gerade nicht fertigstellen. Bitte stellen Sie Ihre Frage gleich noch einmal – ich helfe sofort weiter."
3. **Invalid Conversation (404)**: "Diese Konversation wurde nicht gefunden."
4. **Authentication (401)**: "Ihre Sitzung ist abgelaufen. Bitte melden Sie sich erneut an."
5. **Validation (400)**: "Ihre Nachricht ist zu lang. Maximal 4000 Zeichen erlaubt."

**Alternatives Considered**:
1. Don't save user message if AI fails
   - Rejected: Loss of user data, poor UX
2. English error messages
   - Rejected: Inconsistent with German UI

### Decision 5: Frontend State Management

**Chosen**: Local component state (ref) for conversation_id, no Pinia store

**Rationale**:
- Single-page conversation flow doesn't need global state
- Simpler implementation
- No cross-component communication needed
- Clearing chat resets state naturally

**Implementation**:
```typescript
const currentConversationId = ref<string | null>(null)
```

**Alternatives Considered**:
1. Pinia store for conversation state
   - Rejected: Over-engineering for single-page feature
   - Would be useful if conversations need to be accessed from multiple pages
2. URL parameter for conversation_id
   - Rejected: Exposes internal IDs in URL
   - Breaks "new conversation" UX (user would see ID in URL)

## Risks / Trade-offs

### Risk 1: AI Service Latency
**Risk**: Qwen model may take 10-30 seconds to generate responses, users may think system is frozen

**Mitigation**:
- Show animated "Analyse läuft..." loading indicator
- Display typing dots animation
- Consider adding progress messages for very long waits (future enhancement)

**Trade-off**: Longer wait times vs higher quality responses (using trained legal model)

### Risk 2: Rate Limiting False Positives
**Risk**: Legitimate users may hit rate limit during rapid Q&A sessions

**Mitigation**:
- Set reasonable limit (10 messages/minute is generous)
- Clear error message explaining limit
- Easy to adjust limit in future if needed

**Trade-off**: Abuse prevention vs user convenience

### Risk 3: Context Window Limitations
**Risk**: Complex legal questions may need more than 5 messages of context

**Mitigation**:
- 5 messages covers most use cases
- Users can reference previous information in new questions
- Future: Implement smarter context selection (semantic search)

**Trade-off**: Token efficiency vs context completeness

### Risk 4: Database Growth
**Risk**: assistant_messages table will grow rapidly with all conversations

**Mitigation**:
- Add database cleanup job in future (archive old conversations)
- Monitor database size
- Consider adding retention policy (e.g., keep 90 days)

**Trade-off**: Data persistence vs storage costs

## Migration Plan

### Phase 1: Backend Implementation
1. Add database methods to database.py
2. Add `/api/assistant/chat` endpoint to backend-main.py
3. Add rate limiting logic
4. Test endpoint with Postman/curl

### Phase 2: Frontend Integration
1. Update assistant.vue to call new endpoint
2. Add conversation_id state management
3. Update error handling
4. Test locally with dev environment

### Phase 3: Deployment
1. Rebuild backend Docker image
2. Restart backend container (zero downtime - Nginx routes to new container)
3. Rebuild frontend Docker image
4. Restart frontend container (zero downtime)
5. Verify on live site

### Phase 4: Validation
1. Test end-to-end on live site
2. Monitor backend logs for errors
3. Check database for saved messages
4. Monitor AI service latency

### Rollback Plan
If issues arise:
1. Revert backend container to previous image
2. Revert frontend container to previous image
3. Nginx will route to reverted containers
4. No database changes to revert (only new rows added)

**Rollback Time**: ~5 minutes (container restart time)

## Open Questions

1. **Q**: Should we implement conversation titles (auto-generated from first message)?
   **A**: Defer to future enhancement. Not needed for MVP.

2. **Q**: Should we limit conversation length (max messages per conversation)?
   **A**: No hard limit for now. Monitor usage and add if needed.

3. **Q**: Should we implement "regenerate response" feature?
   **A**: Defer to future enhancement. Users can rephrase questions.

4. **Q**: Should we track message tokens for billing/analytics?
   **A**: Yes, but track via analytics_events table (existing pattern). Add in future.

5. **Q**: Should we cache AI responses to save computation?
   **A**: No. Legal advice should be fresh and context-specific. Caching could return stale/incorrect info.

## Success Metrics

### Functional Success
- [ ] Users can send messages and receive AI responses
- [ ] Conversations are persisted to database
- [ ] Multi-turn conversations work with context
- [ ] Rate limiting prevents >10 messages/minute
- [ ] Error messages display in German

### Technical Success
- [ ] Response latency <30 seconds (95th percentile)
- [ ] Error rate <2% (excluding rate limit errors)
- [ ] Zero downtime during deployment
- [ ] No authentication errors for logged-in users

### User Experience Success
- [ ] Clear loading indicators during AI generation
- [ ] Smooth scrolling to new messages
- [ ] Error messages are helpful and actionable
- [ ] Chat history persists across page refreshes (future enhancement)
