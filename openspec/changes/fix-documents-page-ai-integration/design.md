# Design Document - Fix Documents Page AI Integration

## Context

The AnwaltsAI platform's core feature—AI-powered legal document generation—is currently non-functional or unreliable. Users access the documents page at `/documents`, enter requirements, and click "Dokument erzeugen" to generate legal documents. The system should leverage Together AI's `deepcogito/cogito-v2-preview-llama-405B` model to produce high-quality German legal documents.

**Current State:**
- Documents page UI exists and is well-designed
- Backend has Together AI integration code (`ai_service.py`)
- API endpoint `/api/documents/process` routes to document generation
- However, end-to-end flow is broken or untested
- Errors are not properly surfaced to users

**Constraints:**
- Must not break existing OAuth login flow
- Must not disrupt other pages (dashboard, assistant, templates, email, settings)
- Must use existing Together AI account (no provider change)
- Must work within current Docker infrastructure
- Must be deployable by restarting containers (no database migrations)

**Stakeholders:**
- End users (legal professionals) needing reliable document generation
- System administrators monitoring production health
- Development team maintaining the codebase

## Goals / Non-Goals

### Goals
1. **Fix end-to-end document generation** - Users can successfully generate legal documents
2. **Reliable Together AI integration** - Consistent, fast responses from AI service
3. **Excellent error handling** - Clear, actionable error messages for all failure scenarios
4. **Production-ready logging** - Comprehensive logs for troubleshooting without cluttering console
5. **Performance** - Document generation under 10 seconds for typical requests
6. **Backward compatibility** - No breaking changes to existing features

### Non-Goals
1. **UI redesign** - Keep existing documents page design
2. **New features** - Focus only on fixing broken functionality
3. **Provider changes** - Stay with Together AI (no switching to OpenAI, Anthropic, etc.)
4. **Database schema changes** - Work with existing schema
5. **Advanced AI features** - No streaming responses, no fine-tuning (can add later)

## Decisions

### Decision 1: Keep Dual Endpoint Architecture
**What:** Maintain both `/api/ai/generate-document` and `/api/ai/generate-document-simple` with `/api/documents/process` as the unified entry point.

**Why:**
- `/api/documents/process` provides action-based routing (generate vs. submit)
- Existing frontend code expects this endpoint
- Allows future extensibility for different actions
- Provides normalization layer for response formatting

**Alternatives Considered:**
- **Option A:** Direct frontend calls to `/api/ai/generate-document` - Rejected: Requires frontend changes and loses action abstraction
- **Option B:** Merge all endpoints into one - Rejected: Breaks existing API contracts
- **Option C:** Use only generate-document-simple - Rejected: Loses validation from DocumentGenerateRequest model

### Decision 2: Comprehensive Error Response Format
**What:** Standardize error responses across all endpoints with format:
```json
{
  "success": false,
  "error": "User-friendly message",
  "detail": "Technical details",
  "code": "ERROR_CODE",
  "timestamp": "2025-10-18T12:00:00Z"
}
```

**Why:**
- Frontend can reliably parse and display errors
- Users get actionable messages ("Please try again") not technical jargon
- Developers get detailed logs for debugging
- Consistent pattern across all endpoints

**Alternatives Considered:**
- **Option A:** HTTPException only - Rejected: Frontend can't distinguish error types
- **Option B:** Simple string errors - Rejected: Not machine-parseable
- **Option C:** FastAPI's default error format - Rejected: Too technical for end users

### Decision 3: Add AI Health Check Endpoint
**What:** Create `/health/ai` endpoint that tests Together AI connectivity with simple request.

**Why:**
- Allows monitoring systems to detect AI service issues independently
- Can be called pre-generation to check availability
- Provides diagnostic information (latency, model status)
- Separates AI health from database/Redis health

**Implementation:**
```python
@app.get("/health/ai")
async def health_check_ai():
    try:
        start = time.time()
        response = await ai_service.generate_completion(
            prompt="Test",
            model=ai_service.together_model,
            max_tokens=10,
            temperature=0.1,
            fail_hard=True
        )
        latency_ms = int((time.time() - start) * 1000)
        return {
            "status": "healthy",
            "provider": ai_service.provider,
            "model": response.model or ai_service.together_model,
            "latency_ms": latency_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "provider": ai_service.provider,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
```

### Decision 4: Frontend Logging Strategy
**What:** Add console logging for document generation flow but make it toggleable via localStorage flag.

**Why:**
- Essential for debugging production issues
- Users can enable "debug mode" if they encounter problems
- Doesn't clutter normal user console
- Can be remotely enabled for support sessions

**Implementation:**
```javascript
const DEBUG = localStorage.getItem('anwalts_debug') === 'true'
function debugLog(...args) {
  if (DEBUG) console.log('[Documents]', ...args)
}
// Usage:
debugLog('Generating document with payload:', payload)
```

### Decision 5: Timeout Configuration
**What:** Set 60-second timeout for Together AI requests.

**Why:**
- Together AI typically responds in 2-8 seconds for document generation
- 60 seconds allows for occasional API slowness
- Prevents indefinite hangs
- Fast enough that users won't abandon request

**Configuration:**
```python
# ai_service.py
async def _generate_together_completion(...):
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(...)
```

### Decision 6: Response Normalization Layer
**What:** Use `_normalize_document_process_result()` to ensure consistent response format regardless of which internal endpoint was called.

**Why:**
- Frontend expects specific fields: `{success, document: {id, title, content}, processing_state}`
- Different backend functions return slightly different formats
- Normalization ensures frontend parsing never fails
- Single source of truth for response structure

**Fields Guaranteed:**
- `success`: boolean
- `document.id`: UUID or null
- `document.content`: HTML string
- `document.title`: string
- `document.document_type`: string
- `metadata`: object with optional fields
- `processing_state`: "generated" | "submitted" | "error"

## Risks / Trade-offs

### Risk 1: Together AI API Key Exposure
**Risk:** API key is in `.env` file and environment variables.

**Mitigation:**
- Use Docker secrets in future (not implemented yet)
- Ensure `.env` is not committed to git
- Rotate API key if leaked
- Monitor Together AI usage for anomalies

**Trade-off:** Convenience of env vars vs. security of secrets manager

### Risk 2: No Request Rate Limiting
**Risk:** Users can spam document generation, exhausting API quota or causing costs.

**Mitigation:**
- Together AI has built-in rate limits (will return 429)
- Can add Redis-based rate limiting later (planned but not in scope)
- Monitor API usage and set alerts

**Trade-off:** User experience (no artificial limits) vs. cost control

### Risk 3: Large Prompts or Responses
**Risk:** Very long prompts or massive AI responses could cause timeouts or memory issues.

**Mitigation:**
- Limit input field length on frontend (current max: reasonable defaults)
- Set `max_tokens` parameter to Together AI (default: 1000 tokens, ~750 words)
- Monitor token usage in logs
- Can add prompt truncation if needed

**Trade-off:** Flexibility for complex documents vs. performance/reliability

### Risk 4: Caching Stale Responses
**Risk:** Redis cache might serve outdated responses if model behavior changes.

**Mitigation:**
- Cache TTL is 1 hour (reasonable for document generation)
- Cache key includes model name (invalidates on model change)
- Can manually clear cache if needed: `redis-cli FLUSHDB`

**Trade-off:** Performance (cache hits) vs. freshness (always latest model output)

## Migration Plan

### Phase 1: Backend Fixes (30 minutes)
1. Update `ai_service.py` error handling
2. Fix `/api/documents/process` response format
3. Add `/health/ai` endpoint
4. Test with curl commands

### Phase 2: Frontend Fixes (30 minutes)
1. Fix `documents.vue` error handling
2. Add console logging
3. Verify API endpoint configuration
4. Test locally with frontend build

### Phase 3: Build & Deploy (30 minutes)
1. Create backup of current files
2. Build backend Docker image: `docker-compose build anwalts_backend`
3. Build frontend Docker image: `docker-compose build anwalts_frontend`
4. Stop containers: `docker-compose stop anwalts_backend anwalts_frontend`
5. Start containers: `docker-compose up -d anwalts_backend anwalts_frontend`
6. Verify health: `docker ps` and `curl https://portal-anwalts.ai/health`

### Phase 4: Verification (1 hour)
1. Test document generation on live site
2. Test with various inputs (simple, template, upload)
3. Test error scenarios (invalid input, network failure simulation)
4. Verify OAuth still works
5. Verify other pages (dashboard, assistant, etc.) still work
6. Check logs for errors

### Rollback Plan
If issues occur:
1. Stop containers: `docker-compose stop anwalts_backend anwalts_frontend`
2. Restore backup files from `/root/backup/`
3. Rebuild images: `docker-compose build anwalts_backend anwalts_frontend`
4. Restart containers: `docker-compose up -d anwalts_backend anwalts_frontend`
5. Verify rollback successful

**Rollback time:** < 5 minutes

## Open Questions

1. **Q:** Should we add Sentry/error tracking integration?
   **A:** Deferred to future work. Current logging to files is sufficient for now.

2. **Q:** Should we implement streaming responses for real-time document generation?
   **A:** Deferred to future work. Non-streaming is simpler and works well.

3. **Q:** Should we add document generation analytics (time, success rate, etc.)?
   **A:** Deferred to future work. Can add Prometheus metrics later.

4. **Q:** Should we support multiple AI providers (OpenAI, Anthropic)?
   **A:** Out of scope. Focus on fixing Together AI integration first.

5. **Q:** Should we add user-level rate limiting?
   **A:** Deferred to future work. Together AI's rate limits are sufficient for now.

## Success Metrics

### Technical Metrics
- Document generation success rate: **> 95%**
- Average response time: **< 8 seconds**
- Error rate: **< 5%**
- Cache hit rate: **> 30%** (for repeated requests)
- Health check uptime: **> 99%**

### User Experience Metrics
- Users can generate documents without errors
- Error messages are clear and actionable
- No complaints about slow response times
- No regressions in other features

### Monitoring
- Backend logs show successful AI generations
- Browser console shows no errors
- Together AI API usage within expected range
- No 503 errors in production logs

## Future Enhancements

**After this change is deployed and stable:**

1. **Streaming Responses** - Show document generation progress in real-time
2. **Rate Limiting** - Per-user limits to prevent abuse
3. **Advanced Caching** - Smarter cache invalidation, versioning
4. **Error Recovery** - Automatic retry with exponential backoff
5. **A/B Testing** - Test different prompts, models, parameters
6. **Analytics Dashboard** - Visualize generation stats, popular doc types
7. **Model Switching** - Allow admins to switch between Together AI models
8. **Cost Optimization** - Analyze token usage, optimize prompts for cost
9. **Quality Monitoring** - Track document quality scores, user feedback
10. **API Versioning** - Prepare for v2 API with breaking changes

## References

- Together AI API Docs: https://docs.together.ai/reference/chat-completions
- FastAPI Error Handling: https://fastapi.tiangolo.com/tutorial/handling-errors/
- Nuxt 3 Server API: https://nuxt.com/docs/guide/directory-structure/server
- Docker Compose: https://docs.docker.com/compose/
