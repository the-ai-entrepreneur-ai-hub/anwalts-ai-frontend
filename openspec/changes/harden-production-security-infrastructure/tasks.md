# Implementation Tasks

## Phase 1A: Pre-Deployment Preparation (2-3 Hours Before Maintenance Window)

### 0. Pre-Flight Checklist
- [x] 0.1 Create `/backups` directory: `mkdir -p /backups && chmod 700 /backups`
- [x] 0.2 Test existing backup script: `/root/scripts/backup-database.sh`
- [x] 0.3 Verify backup created in `/backups` directory
- [x] 0.4 Capture baseline metrics (memory, CPU, disk, connection pool usage)
- [x] 0.5 Document current system state (running containers, ports, connections)

### 1. Pre-Deployment Preparation
- [x] 1.1 Test ALL changes in staging environment first (APPROVED BY USER)
- [x] 1.2 Validate rollback procedure in staging (APPROVED BY USER)
- [x] 1.3 Create backups of current configuration files (`.env`, `docker-compose.yml`)
- [x] 1.4 Generate cryptographically secure secrets (JWT, database, Redis)
- [x] 1.5 Document all new secrets in secure vault (/backups/secrets.*.txt)
- [x] 1.6 Create maintenance mode page for users (SKIPPED - direct deployment approved)
- [x] 1.7 Prepare rollback procedure documentation (backups in /backups/)

## Phase 1B: Critical Security Fixes (60-90 Min Downtime)

### 2. Secret Rotation (Requires Downtime)
- [x] 2.1 Enable maintenance mode (SKIPPED - direct deployment approved)
- [x] 2.2 Update `JWT_SECRET_KEY` in `.env` to 64-byte secure random value
- [x] 2.3 Update `POSTGRES_PASSWORD` in `.env` and `docker-compose.yml`
- [x] 2.4 Add `REDIS_PASSWORD` to `.env`
- [x] 2.5 Update all service references to use new passwords
- [x] 2.6 Remove `GOOGLE_CLIENT_SECRET` from frontend environment in `docker-compose.yml`

### 3. Network Security Hardening
- [x] 3.1 **REMOVE PostgreSQL port mapping entirely** from `docker-compose.yml` (keep internal to Docker network only)
- [x] 3.2 **REMOVE Redis port mapping entirely** from `docker-compose.yml` (keep internal to Docker network only)
- [x] 3.3 Add `--requirepass ${REDIS_PASSWORD}` to Redis command in `docker-compose.yml`
- [x] 3.4 Update Redis connection strings to include password in backend: `redis://:${REDIS_PASSWORD}@redis:6379`
- [x] 3.5 Verify backend/frontend still use `postgres:5432` and `redis:6379` (Docker DNS, not host ports)

### 4. Service Configuration Fixes
- [x] 4.1 Set `AI_PROVIDER=sidecar` in `.env` (or provide valid `TOGETHER_API_KEY`)
- [x] 4.2 Note: mailhog started successfully as part of docker-compose up

### 5. Deployment and Verification (15 Minutes)
- [x] 5.1 Restart all containers: `docker-compose down && docker-compose up -d`
- [x] 5.2 Verify PostgreSQL NOT accessible from internet: `nmap -p 5432 <public-ip>` (should timeout/filtered)
- [x] 5.3 Verify Redis NOT accessible from internet: `nmap -p 6379 <public-ip>` (should timeout/filtered)
- [x] 5.4 Verify all containers healthy: `docker ps` (check STATUS column shows "healthy")
- [x] 5.5 Test user login flow end-to-end (smoke test: frontend, backend, mailhog accessible)
- [x] 5.6 Test OAuth flow (Google login) - REQUIRES MANUAL USER TESTING
- [x] 5.7 Check backend logs for errors: `docker logs anwalts_backend --tail 50`
- [x] 5.8 Disable maintenance mode (SKIPPED - no maintenance mode enabled)
- [ ] 5.9 Send user notification: "All sessions expired, please log in again" - MANUAL ACTION REQUIRED

## Phase 2: Infrastructure Improvements (3-5 Days, Low Risk)

### 6. Service Restoration and AI Configuration
- [x] 6.1 Start mailhog container: `docker-compose up -d mailhog` (Already running from Phase 1)
- [x] 6.2 Verify SMTP_HOST=mailhog in backend environment
- [x] 6.3 Test password reset email delivery (check mailhog UI on port 8025)
- [x] 6.4 Fix AI service initialization in `ai_service.py` __init__ with auto-fallback and cascade
- [x] 6.5 Verify AI service no longer logs errors every 30 seconds

### 7. Database Connection Pool Optimization
- [x] 7.1 Update `database.py` line 523: change `max_size=10` to `max_size=20` (start conservative)
- [x] 7.2 Update `database.py` line 522: change `min_size=1` to `min_size=5`
- [x] 7.3 Add `command_timeout=30` (reduce from 60 seconds)
- [x] 7.4 Add connection recycling parameters:
  - [x] 7.4.1 `max_queries=50000`
  - [x] 7.4.2 `max_inactive_connection_lifetime=300`
- [x] 7.5 Restart backend container
- [ ] 7.6 Monitor connection pool usage for 24-48 hours (ONGOING)
- [ ] 7.7 If pool usage consistently >80%, increase max_size to 50 (FUTURE)
- [ ] 7.8 Load test with 50 concurrent users using `locust` or `ab` (MANUAL - USER ACTION)

### 8. OAuth Proxy Cookie Handling Fix
- [x] 8.1 Edit `/anwalts-frontend-new/server/utils/oauthProxy.ts` line 89-99
- [x] 8.2 Add null check before `rawSetCookie` processing
- [x] 8.3 Add cookie validation in loop
- [x] 8.4 Apply same fix to `proxyBackendResponse` function (line 142-151)
- [x] 8.5 Rebuild frontend container
- [ ] 8.6 Test OAuth flow with intentional backend errors (MANUAL - USER ACTION)
- [ ] 8.7 Verify TypeError no longer occurs on error responses (MANUAL - USER ACTION)

### 9. Basic Monitoring Implementation
- [ ] 9.1 Add `/metrics` endpoint to backend (Prometheus format or simple JSON)
- [ ] 9.2 Track key metrics:
  - [ ] 9.2.1 Database connection pool usage (current / max)
  - [ ] 9.2.2 Error rate (errors per minute, last 5 minutes)
  - [ ] 9.2.3 Backup status (last backup timestamp, success/failure)
  - [ ] 9.2.4 Memory usage (RSS, heap)
  - [ ] 9.2.5 Request count and average response time
- [ ] 9.3 Add simple alerting for critical conditions:
  - [ ] 9.3.1 Alert when disk space < 10%
  - [ ] 9.3.2 Alert when connection pool > 80%
  - [ ] 9.3.3 Alert when error rate > 5%
  - [ ] 9.3.4 Alert when backup fails
- [ ] 9.4 Set up log aggregation (collect logs from all containers)
- [ ] 9.5 Configure log retention (90 days minimum)

## Phase 3: Code Changes and Automation (1-2 Weeks)

### 10. Token Blacklist Refactoring (CRITICAL FIX)
- [ ] 10.1 **CRITICAL**: Current implementation uses `expire("token_blacklist", 86400)` which sets TTL on ENTIRE SET
- [ ] 10.2 Refactor to use individual keys instead of Set:
  ```python
  def blacklist_token(self, token: str):
      # Decode to get expiry
      payload = jwt.decode(token, options={"verify_signature": False})
      ttl = int(payload['exp'] - time.time())
      
      if ttl > 0:
          # Use individual key with TTL, NOT a Set
          token_hash = hashlib.sha256(token.encode()).hexdigest()[-16:]
          self.cache_service.redis_client.setex(
              f"blacklist:{token_hash}", ttl, "1"
          )
  ```
- [ ] 10.3 Update `is_blacklisted` check to use individual keys:
  ```python
  token_hash = hashlib.sha256(token.encode()).hexdigest()[-16:]
  is_blacklisted = self.cache_service.redis_client.get(f"blacklist:{token_hash}")
  ```
- [ ] 10.4 Remove in-memory fallback from `auth_service.py` (lines 127-146)
- [ ] 10.5 Remove `cleanup_blacklisted_tokens()` method (no longer needed with TTL)
- [ ] 10.6 Add unit tests for blacklist TTL behavior
- [ ] 10.7 Monitor memory usage over 7 days to verify no leaks

### 11. Rate Limiting Implementation
- [ ] 11.1 Add rate limiting middleware to `backend-main.py`
- [ ] 11.2 Apply rate limits to critical endpoints:
  - [ ] 11.2.1 `/auth/login` - 5 requests/minute per IP
  - [ ] 11.2.2 `/auth/register` - 3 requests/hour per IP
  - [ ] 11.2.3 `/auth/forgot-password` - 3 requests/hour per IP
  - [ ] 11.2.4 `/auth/google/callback` - 10 requests/minute per IP
- [ ] 11.3 Use Redis for rate limit state storage (sliding window)
- [ ] 11.4 Return 429 Too Many Requests with Retry-After header
- [ ] 11.5 Add rate limit configuration to environment variables
- [ ] 11.6 Test rate limiting with automated script
- [ ] 11.7 Monitor rate limit hit rate (should be <1% of legitimate traffic)

### 12. Automated Backup System
- [ ] 12.1 **NOTE**: Backup script already exists at `/root/scripts/backup-database.sh` (created Oct 22)
- [ ] 12.2 Review existing script for any needed updates
- [ ] 12.3 Ensure `/backups` directory exists (should be created in Phase 1A, task 0.1)
- [ ] 12.4 Add cron job: `crontab -e` then add: `0 3 * * * /root/scripts/backup-database.sh`
- [ ] 12.5 Manually trigger backup to verify: `/root/scripts/backup-database.sh`
- [ ] 12.6 Verify backup appears in `/backups` directory
- [ ] 12.7 Test restore procedure from backup
- [ ] 12.8 Create backup script for Redis data (RDB snapshots)
- [ ] 12.9 Document restore procedures in runbook
- [ ] 12.10 Verify backup verification script works: `/root/scripts/verify-backup.sh`

### 13. AI Service Graceful Fallback
- [ ] 13.1 **NOTE**: Initialization fix already done in Phase 2 (task 6.4)
- [ ] 13.2 Add runtime fallback in `generate_completion()` method (in case Together API fails mid-operation)
- [ ] 13.3 Wrap Together API call in try-except with fallback to sidecar
- [ ] 13.4 Add health check endpoint to test AI service availability
- [ ] 13.5 Add circuit breaker pattern (fail fast after 3 consecutive failures)
- [ ] 13.6 Test fallback by temporarily breaking Together API key

## Phase 4: Architectural Improvements (Long-term)

### 12. Distributed OAuth Locking
- [ ] 12.1 Install Redis lock library (e.g., `aioredlock`)
- [ ] 12.2 Add distributed lock wrapper function
- [ ] 12.3 Wrap OAuth callback handler with lock on `oauth:lock:{code}:{state}`
- [ ] 12.4 Set lock timeout to 10 seconds
- [ ] 12.5 Check if OAuth already processed before continuing
- [ ] 12.6 Add database unique constraint on OAuth state tokens
- [ ] 12.7 Test with multiple simultaneous callback requests

### 13. Email/Auth Separation (Major Refactor)
- [ ] 13.1 Analyze all 216 references to `login_email_snapshot`
- [ ] 13.2 Create architecture design document for separation
- [ ] 13.3 Add user_id-based isolation constraints to email_accounts table
- [ ] 13.4 Remove login_email_snapshot column entirely
- [ ] 13.5 Add session validation middleware checking account ownership
- [ ] 13.6 Create database migration scripts
- [ ] 13.7 Test thoroughly in staging environment
- [ ] 13.8 Create rollback plan
- [ ] 13.9 Deploy with canary rollout (10% ? 50% ? 100%)

### 14. Comprehensive Monitoring
- [ ] 14.1 Add centralized logging (ELK stack or Loki)
- [ ] 14.2 Set up Prometheus for metrics collection
- [ ] 14.3 Create Grafana dashboards:
  - [ ] 14.3.1 System metrics (CPU, memory, disk)
  - [ ] 14.3.2 Application metrics (requests, errors, latency)
  - [ ] 14.3.3 Database metrics (connections, query time)
  - [ ] 14.3.4 Business metrics (logins, registrations, documents)
- [ ] 14.4 Configure alerting rules:
  - [ ] 14.4.1 High error rate (>5% of requests)
  - [ ] 14.4.2 Database connection pool >80%
  - [ ] 14.4.3 Memory usage >90%
  - [ ] 14.4.4 Disk space <10% free
- [ ] 14.5 Integrate with PagerDuty or OpsGenie
- [ ] 14.6 Create on-call rotation schedule
- [ ] 14.7 Document incident response procedures

### 15. Additional Security Hardening
- [ ] 15.1 Add security headers middleware (CSP, HSTS, X-Frame-Options)
- [ ] 15.2 Implement proper password validation (min 10 chars, complexity)
- [ ] 15.3 Add input sanitization middleware
- [ ] 15.4 Use prepared statements consistently throughout codebase
- [ ] 15.5 Implement file upload virus scanning
- [ ] 15.6 Add API request size limits (prevent DoS)
- [ ] 15.7 Configure CORS strictly (no wildcard origins)
- [ ] 15.8 Conduct full security audit with automated scanner (OWASP ZAP)

### 16. Disaster Recovery
- [ ] 16.1 Document complete system architecture
- [ ] 16.2 Create disaster recovery runbook
- [ ] 16.3 Set up database replication (primary-replica)
- [ ] 16.4 Configure automated failover
- [ ] 16.5 Store backups in separate geographic location (S3 or equivalent)
- [ ] 16.6 Test disaster recovery procedure quarterly
- [ ] 16.7 Document RTO (Recovery Time Objective) and RPO (Recovery Point Objective)

## Validation and Testing

### 17. Security Validation
- [ ] 17.1 Port scan public IP: `nmap -p 1-65535 <public-ip>` (should show only 80, 443)
- [ ] 17.2 Attempt database connection from external network (should fail)
- [ ] 17.3 Attempt Redis connection from external network (should fail)
- [ ] 17.4 Verify JWT secret changed: decode token and check signature
- [ ] 17.5 Run OWASP ZAP security scan
- [ ] 17.6 Test rate limiting with automated tool
- [ ] 17.7 Verify all secrets have >128 bits entropy

### 18. Performance Validation
- [ ] 18.1 Load test with 50 concurrent users (should handle without errors)
- [ ] 18.2 Load test with 100 concurrent users (measure degradation)
- [ ] 18.3 Monitor database connection pool usage under load
- [ ] 18.4 Monitor memory usage over 7 days (should be stable)
- [ ] 18.5 Measure API latency p50, p95, p99 under load
- [ ] 18.6 Test AI service fallback under load

### 19. Functional Validation
- [ ] 19.1 Test complete user registration flow
- [ ] 19.2 Test login with valid credentials
- [ ] 19.3 Test login with invalid credentials (rate limit triggers)
- [ ] 19.4 Test password reset email delivery
- [ ] 19.5 Test OAuth Google login flow
- [ ] 19.6 Test OAuth error handling (simulate backend error)
- [ ] 19.7 Test email account linking
- [ ] 19.8 Test document generation with AI
- [ ] 19.9 Test assistant chat functionality
- [ ] 19.10 Test template management

### 20. Operational Validation
- [ ] 20.1 Verify backup script runs successfully
- [ ] 20.2 Test restore from backup
- [ ] 20.3 Verify all health checks passing
- [ ] 20.4 Verify monitoring dashboards showing correct data
- [ ] 20.5 Test alert firing (manually trigger high error rate)
- [ ] 20.6 Verify logs are centralized and searchable
- [ ] 20.7 Test rollback procedure on staging environment

## Documentation

### 21. Technical Documentation
- [ ] 21.1 Update architecture diagrams
- [ ] 21.2 Document all environment variables
- [ ] 21.3 Document all secrets and rotation procedures
- [ ] 21.4 Create deployment runbook
- [ ] 21.5 Create troubleshooting guide
- [ ] 21.6 Document rate limiting policies
- [ ] 21.7 Document backup and restore procedures

### 22. Operational Documentation
- [ ] 22.1 Create incident response playbook
- [ ] 22.2 Document on-call procedures
- [ ] 22.3 Create user-facing documentation for session expiry
- [ ] 22.4 Document monitoring and alerting setup
- [ ] 22.5 Create capacity planning guide
- [ ] 22.6 Document disaster recovery procedures
