# Security Hardening OpenSpec Proposal - Summary

**Proposal ID**: `harden-production-security-infrastructure`  
**Created**: 2025-11-01  
**Status**: ✅ VALIDATED - Ready for Review and Approval  
**Priority**: CRITICAL (Deploy within 24-48 hours)

---

## Executive Summary

A comprehensive OpenSpec proposal has been created addressing **16 CRITICAL vulnerabilities**, **9 HIGH priority issues**, and **12 architectural problems** identified in the production security audit.

**Location**: `/root/openspec/changes/harden-production-security-infrastructure/`

**Validation Status**: ✅ **PASSED** (strict mode)

```bash
cd /root && openspec validate harden-production-security-infrastructure --strict
# Result: Change 'harden-production-security-infrastructure' is valid
```

---

## Proposal Structure

### 📄 Core Documents Created

1. **`proposal.md`** - High-level overview
   - Why: Critical security audit findings
   - What: 16 security/infrastructure changes in 4 phases
   - Impact: Risk assessment, deployment strategy, success metrics

2. **`tasks.md`** - 22 detailed task groups with 165+ individual checkpoints
   - Phase 1: Critical Security (30-minute downtime window)
   - Phase 2: Infrastructure Improvements (rolling restart)
   - Phase 3: Code Changes (testing required)
   - Phase 4: Architectural Improvements (1-3 months)

3. **`design.md`** - Technical design document
   - Context and stakeholder analysis
   - 7 major technical decisions with alternatives considered
   - 5 risks with mitigation strategies
   - 3 trade-off analyses
   - Complete migration plan with rollback procedures
   - 6 open questions with answers

4. **Specification Deltas** (4 new capabilities)

---

## Specification Deltas Overview

### 🔒 `specs/security/spec.md` - New Capability
**5 ADDED Requirements | 18 Scenarios**

- Cryptographic Secret Management (4 scenarios)
  - JWT secret generation (64+ bytes)
  - Database credential security (32+ bytes)
  - Cache credential security (Redis password)
  - Secret rotation invalidates sessions

- Network Port Security (4 scenarios)
  - Database port binding (localhost only)
  - Cache port binding (localhost only)
  - External port scan verification
  - Firewall rule enforcement

- OAuth Client Secret Protection (2 scenarios)
  - Frontend environment isolation
  - OAuth secret usage validation

- Configuration Backup Before Changes (2 scenarios)
  - Pre-deployment configuration backup
  - Rollback capability verification

- Secret Documentation and Storage (2 scenarios)
  - Secret vault storage
  - Secret rotation tracking

### 🏗️ `specs/infrastructure/spec.md` - New Capability
**5 ADDED Requirements | 17 Scenarios**

- Database Connection Pool Sizing (4 scenarios)
  - Production pool configuration (max 50, min 10)
  - Connection pool under load
  - Connection recycling
  - Connection pool monitoring

- Email Service Availability (3 scenarios)
  - Mailhog container operational
  - SMTP connectivity verification
  - Password reset email delivery

- AI Service Configuration and Fallback (4 scenarios)
  - Together AI configuration
  - Sidecar AI fallback
  - AI provider explicit configuration
  - AI health check reporting

- Redis Password Authentication (3 scenarios)
  - Redis server authentication requirement
  - Backend Redis authentication
  - Redis authentication failure handling

- Service Health Monitoring (3 scenarios)
  - Composite health check
  - Individual service failure reporting
  - All services healthy

### 🔐 `specs/authentication/spec.md` - New Capability
**5 ADDED Requirements | 22 Scenarios**

- Token Blacklist Memory Management (4 scenarios)
  - Redis-based blacklist with TTL
  - In-memory blacklist removal
  - Blacklist cleanup scheduler
  - Blacklist memory stability

- OAuth Callback Error Handling (4 scenarios)
  - Missing Set-Cookie header handling
  - Null cookie value handling
  - OAuth error response propagation
  - Cookie validation before forwarding

- Rate Limiting on Authentication Endpoints (6 scenarios)
  - Login endpoint rate limiting (5/min)
  - Registration endpoint rate limiting (3/hour)
  - Password reset rate limiting (3/hour)
  - OAuth callback rate limiting (10/min)
  - Rate limit state persistence
  - Rate limit configuration

- Distributed OAuth Callback Locking (4 scenarios)
  - OAuth callback lock acquisition
  - Concurrent callback requests
  - OAuth completion check
  - OAuth state uniqueness

- JWT Secret Rotation Impact (3 scenarios)
  - Secret rotation invalidates all tokens
  - Token verification after rotation
  - User notification of rotation

### 📊 `specs/monitoring/spec.md` - New Capability
**6 ADDED Requirements | 24 Scenarios**

- Automated Database Backups (5 scenarios)
  - Daily backup execution (3 AM)
  - Backup retention policy (30 days)
  - Backup storage location
  - Backup script failure handling
  - Backup verification and testing

- Redis Data Backup (2 scenarios)
  - Redis RDB persistence
  - Redis backup schedule

- Comprehensive Health Checks (3 scenarios)
  - Health check endpoint response
  - Health check timeout handling
  - Health check on startup

- Performance Monitoring and Alerting (4 scenarios)
  - Database connection pool monitoring
  - Memory usage monitoring
  - API response time tracking
  - Error rate monitoring

- Centralized Logging (3 scenarios)
  - Log aggregation
  - Log retention policy (90 days)
  - Sensitive data in logs

- Disaster Recovery Documentation (4 scenarios)
  - Recovery runbook accessibility
  - Recovery time objective (RTO: 4 hours)
  - Recovery point objective (RPO: 24 hours)
  - Disaster recovery testing

- Security Monitoring and Audit Logging (4 scenarios)
  - Authentication event logging
  - Rate limit violation logging
  - Configuration change audit logging
  - Suspicious activity detection

---

## Key Technical Decisions

### Decision 1: Simultaneous Secret Rotation
**Rationale**: Single maintenance window minimizes disruption, ensures consistent security posture

### Decision 2: Localhost Port Binding
**Rationale**: Defense in depth - services not accessible from internet at bind level

### Decision 3: Connection Pool 10→50
**Rationale**: Current 10 connections = 20 user capacity, 50 connections = 75+ user capacity

### Decision 4: Redis-Only Token Blacklist
**Rationale**: Automatic TTL expiration, zero memory leaks, distributed state

### Decision 5: OAuth Null-Safe Cookie Handling
**Rationale**: Defensive programming prevents TypeError on backend errors

### Decision 6: AI Cascade Fallback (Together→Sidecar)
**Rationale**: High availability prioritized over response quality

### Decision 7: Redis-Based Rate Limiting
**Rationale**: Simple counter with sliding window sufficient for v1, distributed state

---

## Implementation Phases

### Phase 1: Critical Security (T+0, ~30 min downtime) ⚠️
**Tasks**: 1-5 (Secret rotation, port closure, service fixes)  
**Breaking**: JWT rotation invalidates all sessions  
**Risk**: High user impact, complete restart required  
**Success**: Zero public port exposure, cryptographic secrets

### Phase 2: Infrastructure (T+24h, rolling restart)
**Tasks**: 6-7 (Connection pool, OAuth proxy, mailhog, AI config)  
**Breaking**: None  
**Risk**: Low, code fixes only  
**Success**: 50+ concurrent user support, email functional

### Phase 3: Code Changes (T+1 week, testing required)
**Tasks**: 8-11 (Token cleanup, rate limiting, backups, AI fallback)  
**Breaking**: None  
**Risk**: Medium, requires thorough testing  
**Success**: Memory stable, backups automated, brute force prevented

### Phase 4: Architectural (T+1 month, phased rollout)
**Tasks**: 12-16 (Email/auth separation, distributed locks, monitoring)  
**Breaking**: None (feature flags for gradual rollout)  
**Risk**: High complexity, requires canary deployment  
**Success**: Zero session hijacking, zero OAuth race conditions

---

## Testing & Validation Checklist

### Security Validation (17 checks)
- [ ] Port scan shows only 80, 443 open
- [ ] Database connection from external network fails
- [ ] Redis connection from external network fails
- [ ] JWT tokens use new secret
- [ ] OWASP ZAP security scan passes
- [ ] Rate limiting blocks brute force attempts
- [ ] All secrets >128 bits entropy

### Performance Validation (6 checks)
- [ ] 50 concurrent users handled without errors
- [ ] 100 concurrent users measured (degradation acceptable)
- [ ] Database connection pool <80% under load
- [ ] Memory usage stable over 7 days
- [ ] API latency p95 <2 seconds
- [ ] AI fallback works under load

### Functional Validation (10 checks)
- [ ] User registration completes
- [ ] Login with valid credentials works
- [ ] Login with invalid credentials rate-limited
- [ ] Password reset email delivered
- [ ] OAuth Google login completes
- [ ] OAuth error handling (no TypeError)
- [ ] Email account linking works
- [ ] Document generation with AI works
- [ ] Assistant chat functional
- [ ] Template management works

### Operational Validation (7 checks)
- [ ] Backup script runs successfully
- [ ] Restore from backup tested
- [ ] All health checks passing
- [ ] Monitoring dashboards show correct data
- [ ] Alerts fire correctly
- [ ] Logs centralized and searchable
- [ ] Rollback procedure tested in staging

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| User disruption from JWT rotation | High | Medium | Off-hours deployment, clear messaging, support prep |
| Database password update failure | Low | High | Staging test, rollback scripts ready |
| Redis auth breaking connections | Low | Medium | Test in health check, graceful degradation |
| Backup script silent failures | Medium | High | Verification, alerts, weekly restore tests |
| Rate limiting false positives | Medium | Medium | Conservative limits, whitelist, monitoring |

---

## Success Metrics

### Immediate (Phase 1)
- ✅ Zero publicly exposed ports (5432, 6379)
- ✅ Cryptographically secure secrets (64+ bytes)
- ✅ All health checks passing
- ✅ Users can log in successfully

### Short-term (Phase 2-3)
- ✅ 50+ concurrent users supported
- ✅ Email delivery functional
- ✅ Memory usage stable over 7 days
- ✅ Automated daily backups

### Long-term (Phase 4)
- ✅ Zero session hijacking incidents (30 days)
- ✅ Zero OAuth duplicate users
- ✅ Comprehensive monitoring operational
- ✅ Disaster recovery tested

---

## Estimated Effort

| Phase | Timeline | Effort | Team Size |
|-------|----------|--------|-----------|
| Phase 1 | 24-48 hours | 3-4 hours | 1 engineer |
| Phase 2 | 3-5 days | 2-3 hours | 1 engineer |
| Phase 3 | 1-2 weeks | 1-2 days | 1 engineer |
| Phase 4 | 1-3 months | 2-3 weeks | 2 engineers |

**Total Technical Debt**: 6-12 months to address all 62 issues

---

## Next Steps

### 1. Review and Approval
- [ ] Security team reviews proposal
- [ ] Operations team reviews deployment plan
- [ ] Stakeholders approve breaking changes (JWT rotation)
- [ ] Management approves maintenance window

### 2. Pre-Deployment
- [ ] Test all changes in staging environment
- [ ] Create rollback scripts
- [ ] Generate and vault all new secrets
- [ ] Schedule maintenance window (low-traffic hours)
- [ ] Notify users 24 hours in advance

### 3. Deployment
- [ ] Execute Phase 1 (critical security)
- [ ] Monitor for 48 hours
- [ ] Execute Phase 2 (infrastructure)
- [ ] Monitor for 1 week
- [ ] Execute Phase 3 (code changes)
- [ ] Plan Phase 4 (architectural)

### 4. Validation
- [ ] Run complete test suite
- [ ] Perform security audit
- [ ] Load test under realistic conditions
- [ ] Document lessons learned

---

## OpenSpec Commands Reference

```bash
# View proposal details
openspec show harden-production-security-infrastructure

# View specific spec delta
openspec show harden-production-security-infrastructure --json --deltas-only

# View delta differences
openspec diff harden-production-security-infrastructure

# Validate proposal
openspec validate harden-production-security-infrastructure --strict

# After deployment: Archive the change
openspec archive harden-production-security-infrastructure --yes

# This will:
# - Move changes/ to changes/archive/2025-11-01-harden-production-security-infrastructure/
# - Update specs/ with new capabilities (security, infrastructure, authentication, monitoring)
```

---

## File Locations

```
/root/openspec/changes/harden-production-security-infrastructure/
├── proposal.md                           # High-level overview
├── tasks.md                              # 22 task groups, 165+ checkpoints
├── design.md                             # Technical design document
└── specs/
    ├── security/spec.md                  # 5 requirements, 18 scenarios
    ├── infrastructure/spec.md            # 5 requirements, 17 scenarios
    ├── authentication/spec.md            # 5 requirements, 22 scenarios
    └── monitoring/spec.md                # 6 requirements, 24 scenarios
```

---

## Breaking Changes Summary

⚠️ **CRITICAL BREAKING CHANGES IN PHASE 1**:

1. **JWT Secret Rotation**
   - **Impact**: All user sessions invalidated
   - **Action Required**: All users must re-login
   - **Notification**: Email 24h before, in-app message during
   - **Mitigation**: Off-hours deployment, support team ready

2. **Database Password Change**
   - **Impact**: Requires complete container restart
   - **Action Required**: 30-minute maintenance window
   - **Notification**: Maintenance mode page
   - **Mitigation**: Rollback scripts tested

3. **Port Closures**
   - **Impact**: External database/Redis tools won't work
   - **Action Required**: Use SSH tunnel for admin access
   - **Notification**: Document in operations runbook
   - **Mitigation**: None expected (no external connections should exist)

---

## Contact & Escalation

**Proposal Owner**: System Administrator  
**Security Lead**: [To be assigned]  
**Operations Lead**: [To be assigned]  

**Escalation Path**:
1. Technical issues → Engineering team
2. Security concerns → Security team
3. User impact concerns → Product team
4. Deployment approval → Management

---

## Approval Signatures

- [ ] **Security Team**: Approved / Rejected  
  Name: _______________ Date: ___________

- [ ] **Operations Team**: Approved / Rejected  
  Name: _______________ Date: ___________

- [ ] **Engineering Lead**: Approved / Rejected  
  Name: _______________ Date: ___________

- [ ] **Management**: Approved / Deployment Window Confirmed  
  Name: _______________ Date: ___________

---

**Status**: ✅ PROPOSAL COMPLETE - AWAITING APPROVAL

**Do Not Implement Until Approved**

Once approved, implementation should begin with Phase 1 within 24-48 hours to address CRITICAL security vulnerabilities.
