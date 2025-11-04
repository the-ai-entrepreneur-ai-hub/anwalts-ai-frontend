# Production Security Hardening - Design Document

## Context

### Background
Production security audit (2025-11-01) identified critical vulnerabilities in the deployed system at 148.x.x.222 (28 days uptime, stable operation, 124GB RAM with 10% utilization):
- **16 CRITICAL issues** requiring immediate action
- **9 HIGH priority issues** requiring short-term fixes  
- **12 architectural problems** requiring long-term refactoring

The system is currently **NOT production-ready** from a security perspective.

### Current State
- JWT secret: `dev-only-jwt-secret` (publicly known development default)
- Database password: `anwalts_password` (default, predictable)
- PostgreSQL exposed on public port 5432 (no firewall)
- Redis exposed on public port 6379 (no authentication)
- OAuth client secret in frontend environment (should be backend-only)
- Database connection pool: 10 connections (exhausts at ~20 concurrent users)
- Mailhog container not running (password resets broken)
- AI_PROVIDER=together but TOGETHER_API_KEY empty (AI service degraded)
- Token blacklist grows unbounded in memory (never cleaned)
- OAuth proxy bug causes TypeError on error responses

### Stakeholders
- **Users**: Affected by session invalidation, require re-login notification
- **Operations**: Responsible for deployment, monitoring, incident response
- **Security**: Responsible for audit compliance, secret management
- **Development**: Responsible for implementing code changes, testing

### Constraints
- **Downtime requirement**: Phase 1 requires brief maintenance window (~30 minutes)
- **User impact**: JWT rotation invalidates all sessions (unavoidable)
- **Budget**: Must use existing infrastructure, no new paid services for Phase 1-3
- **Timeline**: CRITICAL fixes must deploy within 24-48 hours
- **Compliance**: GDPR requires proper data security and breach prevention

## Goals / Non-Goals

### Goals
1. **Eliminate CRITICAL security vulnerabilities** within 24-48 hours
2. **Prevent data breach** through proper secret management and network isolation
3. **Restore email functionality** for password resets
4. **Scale to 100+ concurrent users** without connection pool exhaustion
5. **Establish baseline monitoring** and backup procedures
6. **Create foundation for long-term architectural improvements**

### Non-Goals
1. **Complete architectural refactor** (email/auth separation) - Phase 4, long-term
2. **Full observability stack** (ELK, Prometheus, Grafana) - Phase 4, optional enhancement
3. **Multi-region deployment** or geo-redundancy - future consideration
4. **Zero-downtime deployment** for Phase 1 - acceptable brief outage for security
5. **Automated security scanning** integration - Phase 4, operational improvement

## Decisions

### Decision 1: Secret Rotation Strategy
**Decision**: Rotate ALL production secrets (JWT, database, Redis) simultaneously in single maintenance window.

**Rationale**:
- Minimizes total downtime (one outage vs. multiple)
- Ensures consistent security posture across all services
- Reduces coordination complexity
- Users only disrupted once (re-login required anyway for JWT rotation)

**Alternatives Considered**:
1. **Rolling secret rotation** - Rejected: More complex, multiple disruptions, harder to coordinate
2. **JWT rotation only** - Rejected: Leaves other vulnerabilities exposed, doesn't address root cause
3. **Delay database password rotation** - Rejected: Database exposure is CRITICAL risk

**Implementation**:
```bash
# Generate secrets
JWT_SECRET=$(openssl rand -base64 64 | tr -d '\n' | head -c 64)
DB_PASSWORD=$(openssl rand -base64 32 | tr -d '\n')
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d '\n')

# Update .env
sed -i "s/^JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET/" .env
sed -i "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$DB_PASSWORD/" .env
echo "REDIS_PASSWORD=$REDIS_PASSWORD" >> .env

# Update docker-compose.yml with new passwords
# Restart all containers
docker-compose down && docker-compose up -d
```

### Decision 2: Port Binding Strategy
**Decision**: Bind PostgreSQL and Redis to localhost (127.0.0.1) only, not Docker network IP.

**Rationale**:
- Simplest security model: services only accessible from host machine
- No firewall rules needed within Docker network (containers can still communicate)
- External access completely prevented at bind level
- Standard security best practice

**Alternatives Considered**:
1. **Firewall rules only** - Rejected: Defense in depth principle, prefer bind-level restriction
2. **Docker network isolation** - Considered: Additional layer, but bind restriction is sufficient
3. **VPN requirement** - Rejected: Overkill for single-server deployment

**Implementation**:
```yaml
# docker-compose.yml
postgres:
  ports:
    - "127.0.0.1:5432:5432"  # Localhost only
redis:
  ports:
    - "127.0.0.1:6379:6379"  # Localhost only
```

**Compatibility Check**:
- Backend container: Uses `postgres:5432` (Docker network DNS) - ✅ Unaffected
- Redis client: Uses `redis:6379` (Docker network DNS) - ✅ Unaffected
- External tools: Must use SSH tunnel - ⚠️ Change (document in runbook)

### Decision 3: Database Connection Pool Sizing
**Decision**: Increase max_size from 10 to 20 initially, monitor, then scale to 50 if needed. Increase min_size from 1 to 5.

**Rationale**:
- **Current**: 10 connections pooled across ALL requests (not per-endpoint)
- **Analysis**: Claim of "system fails at ~20 concurrent users" lacks supporting data
- **Conservative Approach**: Double pool size initially (10 → 20) to provide headroom
- **Monitor First**: Track connection pool utilization for 24-48 hours under load
- **Scale Up**: If pool consistently >80% utilized, increase to 50

**Alternatives Considered**:
1. **max_size=50 immediately** - Rejected: Over-allocation without data, wastes resources
2. **max_size=100** - Rejected: Excessive for single PostgreSQL instance, may overload database
3. **Dynamic scaling** - Future: Consider for multi-instance deployment

**Trade-offs**:
- **Pro**: Eliminates connection pool exhaustion under normal load
- **Pro**: Supports expected user growth (current: ~20 users, target: 100 users)
- **Con**: Higher memory usage per connection (~10MB per connection = 500MB total)
- **Con**: PostgreSQL may need tuning (max_connections default is 100)

**Monitoring**:
- Track connection pool usage percentage
- Alert when >80% utilized
- Plan for horizontal scaling if consistently above 70%

### Decision 4: Token Blacklist Architecture
**Decision**: Refactor from Redis Set with single TTL to individual keys with per-token TTL.

**Rationale**:
- **CRITICAL BUG DISCOVERED**: Current code uses `redis.expire("token_blacklist", 86400)` which sets TTL on ENTIRE SET
- **Impact**: When set expires, ALL blacklisted tokens become valid again (security breach)
- **Root cause**: Using Set (SADD) instead of individual keys (SETEX)
- **Solution**: Individual keys with TTL calculated from JWT expiry time

**Implementation**:
```python
def blacklist_token(self, token: str):
    if not self.cache_service or not self.cache_service.redis_client:
        raise RuntimeError("Redis required for token blacklisting")
    
    # Decode token to get expiry
    payload = jwt.decode(token, options={"verify_signature": False})
    ttl = int(payload['exp'] - time.time())
    
    if ttl > 0:
        # Use individual key with per-token TTL (NOT a Set)
        import hashlib
        token_hash = hashlib.sha256(token.encode()).hexdigest()[-16:]
        self.cache_service.redis_client.setex(
            f"blacklist:{token_hash}", ttl, "1"
        )
```

**Alternatives Considered**:
1. **Keep in-memory + periodic cleanup** - Rejected: Still has memory leak risk, requires careful scheduling
2. **Database table** - Rejected: Slower than Redis, needs separate cleanup job
3. **Token versioning** - Future: Consider for more sophisticated invalidation

**Trade-offs**:
- **Pro**: Zero memory leaks, automatic per-token cleanup
- **Pro**: Distributed state (works with multiple backend instances)
- **Pro**: No periodic cleanup scheduler needed
- **Con**: Hard dependency on Redis (acceptable, already required)
- **Con**: Blacklist lost on Redis restart (acceptable, tokens expire naturally within 24 hours)

### Decision 5: OAuth Proxy Error Handling
**Decision**: Add null checks and validation before cookie forwarding in frontend proxy.

**Rationale**:
- **Current bug**: TypeError when backend returns error without Set-Cookie header
- **Root cause**: Code assumes rawSetCookie always valid, doesn't handle null/undefined
- **Impact**: Breaks entire OAuth flow on any backend error

**Implementation**:
```typescript
// Safe cookie forwarding
const rawSetCookie = typeof response.headers.getSetCookie === 'function'
  ? response.headers.getSetCookie()
  : response.headers.get('set-cookie')

// Early return if no cookies
if (!rawSetCookie) {
  const status = response.status && response.status !== 0 ? response.status : 302
  return sendRedirect(event, location, status)
}

// Parse and validate
const setCookies = Array.isArray(rawSetCookie)
  ? rawSetCookie
  : typeof rawSetCookie === 'string'
    ? splitCookiesString(rawSetCookie)
    : []

// Filter out invalid cookies
for (const cookie of setCookies) {
  if (cookie && typeof cookie === 'string' && cookie.trim().length > 0) {
    appendResponseHeader(event, 'set-cookie', cookie)
  }
}
```

**Alternatives Considered**:
1. **Try-catch wrapper** - Rejected: Hides errors, doesn't fix root cause
2. **Backend fix only** - Rejected: Frontend should be defensive, handle invalid input
3. **Remove cookie forwarding** - Rejected: Breaks OAuth session management

### Decision 6: AI Service Fallback Strategy
**Decision**: Implement cascade fallback (Together → sidecar) with warning logging.

**Rationale**:
- **Current**: AI_PROVIDER=together but TOGETHER_API_KEY empty = 100% failure rate
- **Issue**: No graceful degradation, every AI request fails
- **Solution**: Attempt Together, fall back to sidecar on any error

**Implementation**:
```python
async def generate_completion(self, prompt: str, **kwargs):
    # Try Together if configured
    if self.provider == "together" and self.together_api_key:
        try:
            return await self._generate_together_completion(prompt, **kwargs)
        except Exception as e:
            logger.warning(f"Together AI failed, falling back to sidecar: {e}")
    
    # Always fall back to sidecar
    return await self._generate_sidecar_completion(prompt, **kwargs)
```

**Alternatives Considered**:
1. **Require explicit provider** - Rejected: Reduces availability, no graceful degradation
2. **Load balancing** - Future: Consider for performance optimization
3. **Circuit breaker** - Future: Add after basic fallback working

**Trade-offs**:
- **Pro**: High availability, system never fails due to Together API issues
- **Pro**: Transparent to users, same API interface
- **Con**: Sidecar slower than Together (acceptable for availability)
- **Con**: May mask Together API issues (mitigated by warning logs)

### Decision 7: Rate Limiting Implementation
**Decision**: Use simple Redis-based counter with sliding window for each endpoint/IP combination.

**Rationale**:
- **Need**: Prevent brute force, account enumeration, DoS attacks
- **Simplicity**: Redis INCR + EXPIRE is sufficient for v1
- **State**: Distributed across multiple backend instances

**Implementation**:
```python
async def rate_limit_check(ip: str, endpoint: str, limit: int, window: int):
    key = f"rl:{endpoint}:{ip}"
    count = redis.incr(key)
    if count == 1:
        redis.expire(key, window)
    
    if count > limit:
        raise HTTPException(
            status_code=429,
            headers={"Retry-After": str(window)}
        )
```

**Limits**:
- `/auth/login`: 5 requests/minute per IP
- `/auth/register`: 3 requests/hour per IP
- `/auth/forgot-password`: 3 requests/hour per IP
- `/auth/google/callback`: 10 requests/minute per IP

**Alternatives Considered**:
1. **Token bucket algorithm** - Future: More sophisticated, not needed for v1
2. **Per-user rate limiting** - Future: Better for authenticated endpoints
3. **slowloris library** - Rejected: Adds dependency, simple solution sufficient

## Risks / Trade-offs

### Risk 1: User Disruption from JWT Rotation
**Risk**: All users forced to re-login simultaneously may overwhelm support.

**Mitigation**:
- Deploy during low-traffic hours (3 AM - 5 AM local time)
- Display clear message: "Security update required. Please log in again."
- Prepare support team with FAQ
- Send email notification 24 hours before deployment
- Monitor login endpoint load, scale if needed

**Likelihood**: High (100% of active users affected)  
**Impact**: Medium (temporary inconvenience, no data loss)  
**Severity**: Medium

### Risk 2: Database Connection String Update Failures
**Risk**: Services fail to start if database password update incomplete.

**Mitigation**:
- Test in staging environment first
- Create checklist of all locations requiring password update
- Use environment variable substitution consistently
- Verify all containers healthy before exiting maintenance
- Keep rollback scripts ready

**Likelihood**: Low (straightforward change, tested in staging)  
**Impact**: High (complete service outage)  
**Severity**: Medium

### Risk 3: Redis Authentication Breaking Existing Connections
**Risk**: Backend cache operations fail if Redis password not properly configured.

**Mitigation**:
- Update connection strings before restarting Redis
- Test Redis connectivity in health check
- Monitor cache hit rates after deployment
- Redis fallback already exists in code (degrades gracefully)

**Likelihood**: Low (well-documented change)  
**Impact**: Medium (performance degradation, no data loss)  
**Severity**: Low

### Risk 4: Backup Script Failures
**Risk**: Automated backups fail silently, no backups for 30 days before detection.

**Mitigation**:
- Implement backup verification (file size check, PostgreSQL restore test)
- Alert on backup failures via monitoring
- Manual backup before Phase 1 deployment
- Test restore procedure weekly for first month

**Likelihood**: Medium (cron jobs often fail silently)  
**Impact**: High (no recovery from data loss)  
**Severity**: High

**Action**: Add this to Phase 3 implementation checklist with extra validation.

### Risk 5: Rate Limiting False Positives
**Risk**: Legitimate users blocked by aggressive rate limits (e.g., corporate NAT).

**Mitigation**:
- Start with conservative limits, tighten based on observed abuse
- Implement whitelist for known good IPs
- Provide clear error message with support contact
- Monitor rate limit hit rate, adjust if >1% of legitimate traffic

**Likelihood**: Medium (NAT scenarios common in corporate environments)  
**Impact**: Medium (users temporarily blocked, but can retry)  
**Severity**: Low-Medium

### Trade-off 1: Security vs. Convenience
**Trade-off**: JWT rotation invalidates sessions for user security, but inconveniences users.

**Decision**: Prioritize security. User re-login is acceptable cost for fixing critical vulnerability.

**Justification**: Development JWT secret in production is complete authentication bypass. User inconvenience is temporary, security breach is permanent reputation damage.

### Trade-off 2: Performance vs. Simplicity
**Trade-off**: Could implement connection pooling optimizations (prepared statements, query caching), but increases complexity.

**Decision**: Start with simple connection pool size increase, optimize later if needed.

**Justification**: 50 connections likely sufficient for current scale. Premature optimization adds risk. Monitor first, optimize when data shows bottleneck.

### Trade-off 3: Availability vs. Consistency
**Trade-off**: AI service fallback (Together → sidecar) provides availability but may give different quality responses.

**Decision**: Prioritize availability. Sidecar quality acceptable for degraded mode.

**Justification**: System unusable if AI completely unavailable. Lower quality response better than no response. Users can retry if unsatisfied.

## Migration Plan

### Pre-Migration (T-48 hours)
1. ✅ Create comprehensive backup of production database
2. ✅ Document all current environment variables
3. ✅ Test all changes in staging environment
4. ✅ Create rollback scripts and test rollback procedure
5. ✅ Notify users of scheduled maintenance window
6. ✅ Prepare maintenance mode page
7. ✅ Generate all new secrets and store in vault

### Migration Phase 1B: Critical Security (T-0, 60-90 minutes downtime)
1. **T+0:00** - Enable maintenance mode
2. **T+0:02** - Stop all containers: `docker-compose down`
3. **T+0:03** - Backup current configuration files
4. **T+0:05** - Update `.env` with new secrets (JWT, DB, Redis)
5. **T+0:07** - Update `docker-compose.yml` (ports, Redis auth)
6. **T+0:10** - Start containers: `docker-compose up -d`
7. **T+0:15** - Wait for all health checks to pass
8. **T+0:18** - Verify security: port scan, connection tests
9. **T+0:20** - Smoke test: login, password reset, OAuth
10. **T+0:25** - Disable maintenance mode
11. **T+0:30** - Monitor logs for 30 minutes

### Migration Phase 2: Infrastructure (T+24 hours, 3-5 days, no downtime)
1. Update connection pool settings in `database.py`
2. Fix OAuth proxy in frontend `oauthProxy.ts`
3. Rebuild backend and frontend containers
4. Rolling restart (backend first, then frontend)
5. Start mailhog container
6. Configure AI service (TOGETHER_API_KEY or AI_PROVIDER=sidecar)
7. Verify email delivery, AI service working
8. Load test with 50 concurrent users

### Migration Phase 3: Code Changes (T+1 week, 1-2 weeks)
1. **Refactor Redis blacklist** (CRITICAL: fix Set TTL bug)
2. Deploy rate limiting middleware
3. Deploy AI service fallback logic (runtime protection)
4. Enable automated backup cron job
5. Monitor for 7 days, adjust thresholds

### Migration Phase 4: Architectural (T+1 month, 1-3 months)
1. Design email/auth separation architecture
2. Implement distributed OAuth locking
3. Expand monitoring to full observability stack (Prometheus, Grafana)
4. Gradual rollout with feature flags

### Rollback Procedures

**Rollback Phase 1** (if issues detected in first 30 minutes):
```bash
# Restore configurations
cp .env.backup.YYYYMMDD_HHMMSS .env
cp docker-compose.yml.backup.YYYYMMDD_HHMMSS docker-compose.yml

# Restart with old configs
docker-compose down
docker-compose up -d

# Verify rollback successful
curl http://localhost/health
```

**Rollback Phase 2/3** (code changes):
```bash
# Revert to previous container images
docker-compose down
docker tag anwalts_backend:latest anwalts_backend:previous
docker tag anwalts_backend:backup anwalts_backend:latest
docker-compose up -d
```

**Cannot Rollback**: JWT secret rotation (would invalidate new sessions too). Only forward path: rotate again if issues.

## Known Issues and Corrections

### Issue 1: Redis Blacklist TTL Bug (CRITICAL)
**Original Proposal**: Claimed to fix token blacklist memory leak
**Bug Discovered**: Current implementation uses `redis.expire("token_blacklist", 86400)` which sets TTL on the ENTIRE SET, not individual tokens
**Impact**: When the set expires after 24 hours, ALL blacklisted tokens become valid simultaneously
**Corrected Solution**: Use individual keys with SETEX instead of Set with SADD (documented in tasks 10.1-10.7)

### Issue 2: Port Binding Strategy Ineffective
**Original Proposal**: Bind postgres/redis to `127.0.0.1:5432` in docker-compose.yml
**Reality Check**: Containers communicate via Docker network DNS (`postgres:5432`), not host ports
**Impact**: Port binding to 127.0.0.1 provides NO additional security in Docker context
**Corrected Solution**: Remove port mappings entirely from docker-compose.yml (tasks 3.1-3.2)

### Issue 3: Backup System Already Exists
**Original Proposal**: Create new backup script from scratch
**Discovery**: `/root/scripts/backup-database.sh` already exists (created Oct 22, well-written)
**Missing**: `/backups` directory doesn't exist, cron job not scheduled
**Corrected Solution**: Create directory, schedule existing script (tasks 0.1, 12.4-12.5)

### Issue 4: Connection Pool Sizing Lacks Evidence
**Original Proposal**: Increase max_size from 10 to 50 immediately
**Problem**: Math rationale ("10 ÷ 121 endpoints") is incorrect - pools aren't per-endpoint
**No Data**: No load testing results, monitoring data, or pool exhaustion logs provided
**Corrected Solution**: Conservative increase to 20, monitor 24-48h, scale to 50 only if needed (tasks 7.1-7.7)

### Issue 5: AI Service Using Exception Anti-Pattern
**Original Proposal**: Wrap Together API calls in try-catch for fallback
**Better Design**: Check API key at initialization, reconfigure provider if missing
**Impact**: Eliminates 30-second error log spam currently occurring
**Corrected Solution**: Initialization-time check added to Phase 2 (task 6.4)

### Issue 6: No Monitoring for Phase 1-3 Changes
**Original Proposal**: Deferred all monitoring to Phase 4
**Risk**: Critical changes deployed with no metrics to detect silent failures
**Corrected Solution**: Added Phase 2 task 9 for basic monitoring (pool usage, error rate, backup status)

### Issue 7: Timeline Too Aggressive
**Original Proposal**: 30 minutes downtime for Phase 1
**Reality**: JWT secret in both backend AND frontend, Redis password in connection strings, multiple validation points
**Corrected Timeline**: 60-90 minutes for safe execution with validation

## Open Questions

### Q1: What happens to users mid-session during JWT rotation?
**Answer**: Active WebSocket connections (if any) will be dropped. Users will see "Session expired" on next request. All users must re-login. This is unavoidable and acceptable for security fix.

### Q2: Should we implement canary deployment for Phase 1?
**Answer**: No. Phase 1 requires complete restart (database password change). Canary not possible. Phase 4 (architectural changes) should use canary deployment.

### Q3: What if Together API key becomes available later?
**Answer**: Fallback logic allows setting TOGETHER_API_KEY at runtime. Restart backend container, AI service will use Together, fall back to sidecar if issues. No code changes needed.

### Q4: How to handle database migration if connection pool exhausts during high load?
**Answer**: Migration should happen during low-traffic window (3 AM - 5 AM). If issues arise, rollback is simple (restore old connection pool settings, restart). No data migration, just config change.

### Q5: Should rate limits be per-user or per-IP?
**Answer**: Phase 3 uses per-IP (simpler, protects against unauthenticated attacks). Phase 4 can enhance with per-user limits for authenticated endpoints. Per-IP sufficient for v1.

### Q6: What monitoring tools should we use long-term?
**Answer**: Phase 1-3 use simple health checks and cron-based backups. Phase 4 should evaluate:
- **Logging**: Loki (lighter) vs. ELK stack (more features)
- **Metrics**: Prometheus + Grafana (industry standard)
- **Alerting**: PagerDuty (paid) vs. Alertmanager (free)

Defer decision until Phase 4, gather requirements from Phase 1-3 operational experience.

## Success Criteria

### Phase 1 Success
- ✅ No ports 5432 or 6379 accessible from public internet
- ✅ All secrets cryptographically secure (>128 bits entropy)
- ✅ All containers healthy and passing health checks
- ✅ Users can log in successfully
- ✅ Password reset emails delivered
- ✅ OAuth flow completes without errors
- ✅ Zero security scan findings on exposed services

### Phase 2 Success
- ✅ System handles 50 concurrent users without errors
- ✅ Database connection pool <80% utilized under peak load
- ✅ Mailhog container running, email delivery functional
- ✅ AI service operational (Together or sidecar)
- ✅ OAuth TypeError bug fixed

### Phase 3 Success
- ✅ Memory usage stable over 7 days (no token blacklist growth)
- ✅ Rate limiting prevents brute force (tested with automation)
- ✅ Automated backups running daily
- ✅ Backups verified restorable
- ✅ AI service handles Together API failures gracefully

### Phase 4 Success
- ✅ Zero session hijacking incidents for 30 days
- ✅ Zero duplicate user accounts from OAuth race conditions
- ✅ Monitoring dashboards showing all key metrics
- ✅ Alerting triggers tested and responding correctly
- ✅ Disaster recovery tested and documented

## Timeline

- **Phase 1**: 24-48 hours (CRITICAL, immediate deployment)
- **Phase 2**: 3-5 days (HIGH priority, low risk)
- **Phase 3**: 1-2 weeks (code changes, testing required)
- **Phase 4**: 1-3 months (architectural refactor, can be phased)

**Total Estimated Effort**: 6-12 months to fully address all 62 issues identified in security audit.
