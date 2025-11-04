# Implementation Tasks - Fix Documents Page AI Integration

## 1. Pre-Implementation Verification
- [ ] 1.1 Test Together AI API key with curl command
- [ ] 1.2 Verify environment variables in backend Docker container
- [ ] 1.3 Check current backend logs for AI-related errors
- [ ] 1.4 Test frontend API endpoint URLs and authentication

## 2. Backend AI Service Fixes
- [ ] 2.1 Add comprehensive error handling to `ai_service.generate_document()`
- [ ] 2.2 Improve Together AI error parsing in `_generate_together_completion()`
- [ ] 2.3 Add detailed logging for AI requests and responses
- [ ] 2.4 Add timeout handling for Together AI requests (60s max)
- [ ] 2.5 Verify prompt composition in `compose_document_prompt()`
- [ ] 2.6 Test AI service with sample document generation request

## 3. Backend Document Processing Endpoint Fixes
- [ ] 3.1 Fix `/api/documents/process` response format consistency
- [ ] 3.2 Improve `_normalize_document_process_result()` function
- [ ] 3.3 Add request validation and sanitization
- [ ] 3.4 Ensure proper error responses with status codes
- [ ] 3.5 Fix `generate_document_working()` endpoint response format
- [ ] 3.6 Add comprehensive logging for document processing flow

## 4. Backend Health Check Enhancement
- [ ] 4.1 Add `/health/ai` endpoint to test Together AI connectivity
- [ ] 4.2 Test health endpoint returns proper status codes
- [ ] 4.3 Add AI service status to main `/health` endpoint response

## 5. Frontend API Integration Fixes
- [ ] 5.1 Verify `nuxt.config.ts` API endpoint configuration
- [ ] 5.2 Fix authentication header passing in `generate-document.post.ts`
- [ ] 5.3 Fix authentication header passing in `generate-document-simple.post.ts`
- [ ] 5.4 Add request/response logging in API proxy handlers
- [ ] 5.5 Improve error handling in API proxy endpoints

## 6. Frontend Documents Page Enhancements
- [ ] 6.1 Add comprehensive console logging to `generate()` function
- [ ] 6.2 Improve error message display in UI with actionable info
- [ ] 6.3 Fix `documentAction()` function error handling
- [ ] 6.4 Add loading state improvements with progress indicators
- [ ] 6.5 Handle edge cases (empty response, timeout, rate limit)
- [ ] 6.6 Verify response parsing in `generate()` function

## 7. Environment & Configuration
- [ ] 7.1 Verify `TOGETHER_API_KEY` is set in backend container
- [ ] 7.2 Verify `AI_PROVIDER=together` is set correctly
- [ ] 7.3 Check `TOGETHER_BASE` and `TOGETHER_MODEL` environment vars
- [ ] 7.4 Verify backend can resolve `BACKEND_BASE` URL correctly
- [ ] 7.5 Test Docker network connectivity (frontend ↔ backend)

## 8. Build & Deployment
- [ ] 8.1 Rebuild backend Docker image with changes
- [ ] 8.2 Restart backend container and verify health
- [ ] 8.3 Rebuild frontend Docker image with changes  
- [ ] 8.4 Restart frontend container and verify health
- [ ] 8.5 Verify nginx routing is working correctly
- [ ] 8.6 Check all containers are healthy with `docker ps`

## 9. Testing & Verification
- [ ] 9.1 Test document generation with simple input
- [ ] 9.2 Test document generation with template
- [ ] 9.3 Test document generation with file upload
- [ ] 9.4 Test error handling with invalid inputs
- [ ] 9.5 Test authentication (login, then generate)
- [ ] 9.6 Verify no regressions in OAuth flow
- [ ] 9.7 Verify no regressions in other pages (dashboard, assistant, templates)
- [ ] 9.8 Test export functionality (DOCX, PDF)
- [ ] 9.9 Check browser console for errors
- [ ] 9.10 Check backend logs for errors or warnings

## 10. Performance & Monitoring
- [ ] 10.1 Measure document generation response time
- [ ] 10.2 Test concurrent document generation requests
- [ ] 10.3 Verify Redis caching is working for AI responses
- [ ] 10.4 Check memory usage of backend container
- [ ] 10.5 Monitor Together AI API quota usage

## 11. Documentation & Cleanup
- [ ] 11.1 Document any API changes in code comments
- [ ] 11.2 Add JSDoc comments to new functions
- [ ] 11.3 Remove debug console.log statements (keep important ones)
- [ ] 11.4 Update error messages to be user-friendly
- [ ] 11.5 Archive this OpenSpec change proposal

## Critical Success Checkpoints

### Checkpoint 1: Backend Works
- [ ] Together AI API responds successfully
- [ ] `/api/documents/process` returns well-formed response
- [ ] Backend logs show successful AI generation
- [ ] Health check passes

### Checkpoint 2: Frontend Integration Works
- [ ] Frontend can call backend without authentication errors
- [ ] Response parsing works correctly
- [ ] UI displays generated document
- [ ] Error messages are clear and actionable

### Checkpoint 3: Production Ready
- [ ] All tests pass on live site
- [ ] No errors in browser console
- [ ] No errors in backend logs
- [ ] OAuth and other features still work
- [ ] Document export works (DOCX/PDF)

## Rollback Commands (if needed)

```bash
# Stop and remove containers
docker stop anwalts_backend anwalts_frontend
docker rm anwalts_backend anwalts_frontend

# Restore from backup (if created)
cp /root/backup/backend-main.py /root/backend-main.py
cp /root/backup/ai_service.py /root/ai_service.py
cp /root/backup/documents.vue /root/anwalts-frontend-new/pages/documents.vue

# Restart containers
cd /root && docker-compose up -d anwalts_backend anwalts_frontend

# Verify health
docker ps
curl https://portal-anwalts.ai/health
```

## Notes

- Complete tasks sequentially to catch issues early
- Test after each major checkpoint
- Keep backup of all modified files
- Monitor logs continuously during testing
- Document any unexpected issues encountered
