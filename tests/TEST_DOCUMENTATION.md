# Security Hardening Implementation - Test Documentation

## Overview

This test suite verifies that all security hardening changes from the proposal have been correctly implemented. The tests cover 11 major areas with 70+ individual test cases.

## Test Suite Structure

```
/root/tests/
├── security_hardening_verification.sh    # Master verification script (bash)
├── test_redis_blacklist.py              # Redis blacklist unit tests (pytest)
├── test_connection_pool_load.py         # Connection pool load tests (asyncio)
├── test_oauth_proxy_errors.py           # OAuth error handling tests (requests)
├── run_all_tests.sh                     # Test runner (executes all)
└── TEST_DOCUMENTATION.md                # This file
```

## Quick Start

### Run All Tests
```bash
cd /root/tests
chmod +x *.sh
./run_all_tests.sh
```

### Run Individual Test Suites
```bash
# Master verification (most important)
./security_hardening_verification.sh

# Redis blacklist tests
pytest test_redis_blacklist.py -v

# Connection pool load tests
python3 test_connection_pool_load.py

# OAuth proxy error handling tests
python3 test_oauth_proxy_errors.py
```

## Test Coverage

### 1. Secret Rotation Verification (4 tests)
**Script**: `security_hardening_verification.sh` Section 1

| Test | Description | Success Criteria |
|------|-------------|------------------|
| 1.1 | JWT_SECRET_KEY rotation | Not "dev-only-jwt-secret", ≥64 chars |
| 1.2 | POSTGRES_PASSWORD rotation | Not "anwalts_password", ≥32 chars |
| 1.3 | REDIS_PASSWORD configuration | Configured, ≥32 chars |
| 1.4 | Redis authentication requirement | Requires auth (NOAUTH error) |

**How to Fix Failures**:
- Ensure `.env` file has new secrets
- Restart containers: `docker-compose restart`
- Verify secrets in container: `docker exec anwalts_backend env | grep SECRET`

---

### 2. Network Security Verification (5 tests)
**Script**: `security_hardening_verification.sh` Section 2

| Test | Description | Success Criteria |
|------|-------------|------------------|
| 2.1 | PostgreSQL port 5432 not exposed | Connection timeout/refused |
| 2.2 | Redis port 6379 not exposed | Connection timeout/refused |
| 2.3 | Port mappings removed | No "5432:5432" or "6379:6379" in docker-compose.yml |
| 2.4 | Backend→PostgreSQL connectivity | Can connect via Docker network |
| 2.5 | Backend→Redis connectivity | Can connect via Docker network |

**How to Fix Failures**:
- Remove port mappings from `docker-compose.yml`:
  ```yaml
  postgres:
    # ports: - REMOVE THIS LINE
  redis:
    # ports: - REMOVE THIS LINE
  ```
- Test externally: `nmap -p 5432,6379 <your-public-ip>`

---

### 3. Redis Blacklist Implementation (3 tests)
**Scripts**: `security_hardening_verification.sh` Section 3, `test_redis_blacklist.py`

| Test | Description | Success Criteria |
|------|-------------|------------------|
| 3.1 | Individual keys (not Set) | `blacklist:*` keys exist, not `token_blacklist` Set |
| 3.2 | TTL on individual keys | Keys have TTL >0 |
| 3.3 | In-memory fallback removed | No `self.blacklisted_tokens` Set in auth_service.py |

**Python Unit Tests** (10 additional tests):
- Individual key format verification
- TTL calculation from JWT expiry
- Token hash usage (security)
- GET vs SISMEMBER (individual keys vs Set)
- No in-memory fallback
- Expired token handling
- Redis failure handling
- Key format consistency
- Idempotent operations
- Integration tests with real Redis

**How to Fix Failures**:
- Update `auth_service.py`:
  ```python
  def blacklist_token(self, token: str):
      payload = jwt.decode(token, options={"verify_signature": False})
      ttl = int(payload['exp'] - time.time())
      if ttl > 0:
          token_hash = hashlib.sha256(token.encode()).hexdigest()[-16:]
          self.cache_service.redis_client.setex(f"blacklist:{token_hash}", ttl, "1")
  ```
- Remove `self.blacklisted_tokens: Set[str] = set()` from `__init__`
- Remove `cleanup_blacklisted_tokens()` method

---

### 4. Database Connection Pool Configuration (3 tests)
**Scripts**: `security_hardening_verification.sh` Section 4, `test_connection_pool_load.py`

| Test | Description | Success Criteria |
|------|-------------|------------------|
| 4.1 | max_size updated | ≥20 connections |
| 4.2 | min_size updated | ≥5 connections |
| 4.3 | command_timeout reduced | ≤30 seconds |

**Load Tests** (5 additional tests):
- Concurrent load (50+ concurrent connections)
- Pool exhaustion behavior
- Connection recycling
- Command timeout enforcement
- Sustained load (30s duration)

**How to Fix Failures**:
- Update `database.py`:
  ```python
  self.pool = await asyncpg.create_pool(
      self.connection_string,
      min_size=5,      # Was 1
      max_size=20,     # Was 10
      command_timeout=30  # Was 60
  )
  ```

---

### 5. AI Service Configuration (2 tests)
**Script**: `security_hardening_verification.sh` Section 5

| Test | Description | Success Criteria |
|------|-------------|------------------|
| 5.1 | AI_PROVIDER configuration | If "together", TOGETHER_API_KEY must be set |
| 5.2 | No error log spam | <5 "API key not configured" errors in last 100 logs |

**How to Fix Failures**:
- Update `ai_service.py` `__init__`:
  ```python
  if self.ai_provider == "together" and not self.together_api_key:
      logger.warning("TOGETHER_API_KEY missing, switching to sidecar")
      self.ai_provider = "sidecar"
  ```
- Or set `AI_PROVIDER=sidecar` in `.env`

---

### 6. Mailhog Email Service (3 tests)
**Script**: `security_hardening_verification.sh` Section 6

| Test | Description | Success Criteria |
|------|-------------|------------------|
| 6.1 | Mailhog container running | `docker ps` shows mailhog |
| 6.2 | SMTP configuration | SMTP_HOST=mailhog |
| 6.3 | Web UI accessible | HTTP 200 on localhost:8025 |

**How to Fix Failures**:
- Start mailhog: `docker-compose up -d mailhog`
- Verify: `curl http://localhost:8025`

---

### 7. OAuth Proxy Error Handling (2 tests)
**Scripts**: `security_hardening_verification.sh` Section 7, `test_oauth_proxy_errors.py`

| Test | Description | Success Criteria |
|------|-------------|------------------|
| 7.1 | Null check added | `if (!rawSetCookie)` found in oauthProxy.ts |
| 7.2 | Cookie validation loop | `cookie.trim().length > 0` found in oauthProxy.ts |

**Error Scenario Tests** (6 additional tests):
- Missing Set-Cookie header
- Null cookie values
- Invalid OAuth state
- Expired OAuth code
- Empty cookie strings
- Backend network errors

**How to Fix Failures**:
- Update `/root/anwalts-frontend-new/server/utils/oauthProxy.ts`:
  ```typescript
  if (!rawSetCookie) {
    const status = response.status && response.status !== 0 ? response.status : 302
    return sendRedirect(event, location, status)
  }
  
  for (const cookie of setCookies) {
    if (cookie && typeof cookie === 'string' && cookie.trim().length > 0) {
      appendResponseHeader(event, 'set-cookie', cookie)
    }
  }
  ```

---

### 8. Backup System Verification (4 tests)
**Script**: `security_hardening_verification.sh` Section 8

| Test | Description | Success Criteria |
|------|-------------|------------------|
| 8.1 | /backups directory exists | Directory exists with 700 permissions |
| 8.2 | Backup script exists | /root/scripts/backup-database.sh is executable |
| 8.3 | Cron job scheduled | `crontab -l` shows backup-database.sh |
| 8.4 | Recent backups exist | ≥1 backup file from last 7 days |

**How to Fix Failures**:
- Create directory: `mkdir -p /backups && chmod 700 /backups`
- Schedule cron: `crontab -e` then add: `0 3 * * * /root/scripts/backup-database.sh`
- Test manually: `/root/scripts/backup-database.sh`

---

### 9. Monitoring and Observability (2 tests)
**Script**: `security_hardening_verification.sh` Section 9

| Test | Description | Success Criteria |
|------|-------------|------------------|
| 9.1 | Monitoring endpoint exists | /health or /metrics returns HTTP 200 |
| 9.2 | All containers healthy | No containers with "unhealthy" status |

**How to Fix Failures**:
- Add `/metrics` endpoint to backend
- Implement health checks in docker-compose.yml
- Fix any unhealthy containers: `docker ps -a`

---

### 10. Container Health Status (4 tests)
**Script**: `security_hardening_verification.sh` Section 10

| Test | Description | Success Criteria |
|------|-------------|------------------|
| 10.1 | Backend container healthy | Running + healthy |
| 10.2 | Frontend container healthy | Running + healthy |
| 10.3 | PostgreSQL container healthy | Running + healthy |
| 10.4 | Redis container healthy | Running + healthy |

**How to Fix Failures**:
- Check logs: `docker logs <container_name>`
- Restart unhealthy container: `docker-compose restart <service>`

---

### 11. Secret Security Validation (2 tests)
**Script**: `security_hardening_verification.sh` Section 11

| Test | Description | Success Criteria |
|------|-------------|------------------|
| 11.1 | Frontend secret isolation | GOOGLE_CLIENT_SECRET NOT in frontend env |
| 11.2 | Backend secrets present | GOOGLE_CLIENT_SECRET in backend env |

**How to Fix Failures**:
- Remove GOOGLE_CLIENT_SECRET from frontend environment in docker-compose.yml
- Verify: `docker exec anwalts_frontend env | grep CLIENT_SECRET` (should be empty)

---

## Test Execution Order

1. **Pre-Deployment**: Run tests on staging environment first
2. **Post-Deployment Phase 1B**: Run security_hardening_verification.sh
3. **Post-Deployment Phase 2**: Run connection pool and OAuth tests
4. **Post-Deployment Phase 3**: Run Redis blacklist tests

## Interpreting Results

### Pass Rates

| Pass Rate | Status | Action |
|-----------|--------|--------|
| 100% | ✅ Excellent | All implementations correct |
| 90-99% | ⚠️ Good | Review failed tests, minor issues |
| 80-89% | ⚠️ Fair | Multiple issues, fix before production |
| <80% | ❌ Poor | Critical issues, do not deploy |

### Common Failure Patterns

1. **Secrets Not Rotated**
   - Symptom: Tests 1.1-1.3 fail
   - Fix: Update `.env` and restart containers

2. **Ports Still Exposed**
   - Symptom: Tests 2.1-2.2 fail
   - Fix: Remove port mappings from docker-compose.yml

3. **Redis Blacklist Not Refactored**
   - Symptom: Tests 3.1-3.2 fail
   - Fix: Update auth_service.py to use individual keys

4. **Backup System Not Scheduled**
   - Symptom: Test 8.3 fails
   - Fix: Add cron job

## Performance Benchmarks

### Connection Pool Load Test Expectations

| Metric | Target | Threshold |
|--------|--------|-----------|
| Concurrent connections | 50 | Must handle without errors |
| Query latency (P95) | <500ms | <1000ms acceptable |
| Query latency (P99) | <1000ms | <2000ms acceptable |
| Throughput | >100 q/s | >50 q/s acceptable |
| Error rate | 0% | <1% acceptable |

### Redis Blacklist Performance

| Operation | Target | Threshold |
|-----------|--------|-----------|
| Blacklist operation | <10ms | <50ms acceptable |
| Check operation | <5ms | <20ms acceptable |
| Memory per token | ~100 bytes | <500 bytes acceptable |
| TTL accuracy | ±2 seconds | ±5 seconds acceptable |

## Troubleshooting

### Test Script Won't Run
```bash
chmod +x /root/tests/*.sh
# Check shebang: head -1 security_hardening_verification.sh
```

### Python Tests Fail to Import
```bash
# Install dependencies
pip3 install pytest asyncpg redis requests

# Or use venv
cd /root
source anwalts-backend-venv/bin/activate
pip install -r requirements.txt
```

### Docker Commands Fail
```bash
# Check Docker is running
systemctl status docker

# Check user permissions
groups  # Should include 'docker'
```

### Network Tests Timeout
```bash
# Check if ports are actually exposed
ss -tulpn | grep -E "5432|6379"

# Test from external machine
nmap -p 5432,6379 <public-ip>
```

## CI/CD Integration

### GitLab CI Example
```yaml
test:security-hardening:
  stage: test
  script:
    - cd /root/tests
    - ./security_hardening_verification.sh
  only:
    - main
```

### GitHub Actions Example
```yaml
- name: Run Security Hardening Tests
  run: |
    cd /root/tests
    chmod +x *.sh
    ./run_all_tests.sh
```

## Maintenance

### Updating Tests
1. Edit test files in `/root/tests/`
2. Update this documentation
3. Test changes in staging environment
4. Commit to version control

### Adding New Tests
1. Follow existing test patterns
2. Add to appropriate test file or create new
3. Update TEST_DOCUMENTATION.md
4. Update run_all_tests.sh if needed

## Support

For issues or questions:
1. Check logs: `docker logs <container>`
2. Review test output carefully
3. Consult CRITIQUE_SUMMARY.md for known issues
4. Reference design.md for architecture details

---

**Last Updated**: 2025-11-01  
**Version**: 1.0  
**Test Suite**: Security Hardening Implementation Verification
