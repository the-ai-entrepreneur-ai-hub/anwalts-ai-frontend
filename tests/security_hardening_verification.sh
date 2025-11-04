#!/bin/bash

###############################################################################
# Security Hardening Implementation Verification Script
# Tests all changes from the security hardening proposal
#
# Usage: ./security_hardening_verification.sh
# Returns: 0 if all tests pass, 1 if any test fails
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Configuration
PUBLIC_IP=$(curl -s ifconfig.me || echo "148.x.x.222")
BACKEND_CONTAINER="anwalts_backend"
FRONTEND_CONTAINER="anwalts_frontend"
POSTGRES_CONTAINER="anwalts_postgres"
REDIS_CONTAINER="anwalts_redis"

###############################################################################
# Helper Functions
###############################################################################

log_section() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

log_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    PASSED_TESTS=$((PASSED_TESTS + 1))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    FAILED_TESTS=$((FAILED_TESTS + 1))
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

###############################################################################
# Test 1: Secret Rotation Verification
###############################################################################

test_secret_rotation() {
    log_section "1. Secret Rotation Verification"
    
    # Test 1.1: JWT Secret Changed
    log_test "1.1: Verify JWT_SECRET_KEY is not default value"
    JWT_SECRET=$(docker exec $BACKEND_CONTAINER printenv JWT_SECRET_KEY 2>/dev/null || echo "")
    if [ "$JWT_SECRET" == "dev-only-jwt-secret" ]; then
        log_fail "JWT secret is still using default dev value!"
    elif [ -z "$JWT_SECRET" ]; then
        log_fail "JWT_SECRET_KEY not found in backend environment"
    elif [ ${#JWT_SECRET} -lt 64 ]; then
        log_fail "JWT secret is too short (${#JWT_SECRET} chars, need 64+)"
    else
        log_pass "JWT secret is properly rotated (${#JWT_SECRET} chars)"
    fi
    
    # Test 1.2: Database Password Changed
    log_test "1.2: Verify POSTGRES_PASSWORD is not default value"
    DB_PASSWORD=$(docker exec $BACKEND_CONTAINER printenv POSTGRES_PASSWORD 2>/dev/null || echo "")
    if [ "$DB_PASSWORD" == "anwalts_password" ]; then
        log_fail "Database password is still using default value!"
    elif [ -z "$DB_PASSWORD" ]; then
        log_fail "POSTGRES_PASSWORD not found in backend environment"
    elif [ ${#DB_PASSWORD} -lt 32 ]; then
        log_fail "Database password is too short (${#DB_PASSWORD} chars, need 32+)"
    else
        log_pass "Database password is properly rotated (${#DB_PASSWORD} chars)"
    fi
    
    # Test 1.3: Redis Password Configured
    log_test "1.3: Verify REDIS_PASSWORD is configured"
    REDIS_PASSWORD=$(docker exec $BACKEND_CONTAINER printenv REDIS_PASSWORD 2>/dev/null || echo "")
    if [ -z "$REDIS_PASSWORD" ]; then
        log_fail "REDIS_PASSWORD not found in backend environment"
    elif [ ${#REDIS_PASSWORD} -lt 32 ]; then
        log_fail "Redis password is too short (${#REDIS_PASSWORD} chars, need 32+)"
    else
        log_pass "Redis password is configured (${#REDIS_PASSWORD} chars)"
    fi
    
    # Test 1.4: Redis Requires Authentication
    log_test "1.4: Verify Redis requires authentication"
    if docker exec $REDIS_CONTAINER redis-cli PING 2>&1 | grep -q "NOAUTH"; then
        log_pass "Redis correctly requires authentication"
    elif docker exec $REDIS_CONTAINER redis-cli PING 2>&1 | grep -q "PONG"; then
        log_fail "Redis does NOT require authentication!"
    else
        log_warn "Could not verify Redis authentication requirement"
    fi
}

###############################################################################
# Test 2: Network Security Verification
###############################################################################

test_network_security() {
    log_section "2. Network Security Verification"
    
    # Test 2.1: PostgreSQL Port Not Exposed
    log_test "2.1: Verify PostgreSQL port 5432 is not accessible from internet"
    if timeout 5 bash -c "nc -zv $PUBLIC_IP 5432" 2>&1 | grep -q "succeeded\|open"; then
        log_fail "PostgreSQL port 5432 is ACCESSIBLE from internet!"
    else
        log_pass "PostgreSQL port 5432 is properly secured (not accessible)"
    fi
    
    # Test 2.2: Redis Port Not Exposed
    log_test "2.2: Verify Redis port 6379 is not accessible from internet"
    if timeout 5 bash -c "nc -zv $PUBLIC_IP 6379" 2>&1 | grep -q "succeeded\|open"; then
        log_fail "Redis port 6379 is ACCESSIBLE from internet!"
    else
        log_pass "Redis port 6379 is properly secured (not accessible)"
    fi
    
    # Test 2.3: Port Mappings Removed from docker-compose
    log_test "2.3: Verify port mappings removed from docker-compose.yml"
    if grep -q "5432:5432" /root/docker-compose.yml 2>/dev/null; then
        log_fail "PostgreSQL port mapping still exists in docker-compose.yml"
    elif grep -q "6379:6379" /root/docker-compose.yml 2>/dev/null; then
        log_fail "Redis port mapping still exists in docker-compose.yml"
    else
        log_pass "Port mappings properly removed from docker-compose.yml"
    fi
    
    # Test 2.4: Containers Can Still Communicate
    log_test "2.4: Verify backend can still connect to PostgreSQL via Docker network"
    if docker exec $BACKEND_CONTAINER pg_isready -h postgres -p 5432 -U anwalts_user 2>&1 | grep -q "accepting connections"; then
        log_pass "Backend can connect to PostgreSQL via Docker network"
    else
        log_fail "Backend CANNOT connect to PostgreSQL!"
    fi
    
    log_test "2.5: Verify backend can still connect to Redis via Docker network"
    if docker exec $BACKEND_CONTAINER timeout 3 bash -c "echo PING | nc redis 6379" 2>&1 | grep -q "PONG\|NOAUTH"; then
        log_pass "Backend can connect to Redis via Docker network"
    else
        log_fail "Backend CANNOT connect to Redis!"
    fi
}

###############################################################################
# Test 3: Redis Blacklist Implementation
###############################################################################

test_redis_blacklist() {
    log_section "3. Redis Blacklist Implementation Verification"
    
    # Test 3.1: Check if Using Individual Keys
    log_test "3.1: Verify Redis blacklist uses individual keys (not Set)"
    # Check Redis for blacklist:* pattern keys
    BLACKLIST_KEYS=$(docker exec $REDIS_CONTAINER redis-cli --raw KEYS "blacklist:*" 2>/dev/null | wc -l || echo "0")
    BLACKLIST_SET=$(docker exec $REDIS_CONTAINER redis-cli EXISTS "token_blacklist" 2>/dev/null || echo "0")
    
    if [ "$BLACKLIST_SET" == "1" ]; then
        log_fail "Still using old Set-based blacklist 'token_blacklist'"
    elif [ "$BLACKLIST_KEYS" -gt 0 ]; then
        log_pass "Using individual keys for blacklist ($BLACKLIST_KEYS keys found)"
    else
        log_info "No blacklisted tokens found (system might be new or no logouts)"
    fi
    
    # Test 3.2: Verify TTL on Individual Keys
    log_test "3.2: Verify blacklist keys have TTL set"
    if [ "$BLACKLIST_KEYS" -gt 0 ]; then
        FIRST_KEY=$(docker exec $REDIS_CONTAINER redis-cli --raw KEYS "blacklist:*" 2>/dev/null | head -1)
        if [ -n "$FIRST_KEY" ]; then
            TTL=$(docker exec $REDIS_CONTAINER redis-cli TTL "$FIRST_KEY" 2>/dev/null || echo "-1")
            if [ "$TTL" -gt 0 ]; then
                log_pass "Blacklist keys have TTL set ($TTL seconds remaining on sample key)"
            elif [ "$TTL" == "-1" ]; then
                log_fail "Blacklist key has NO TTL (will never expire)!"
            else
                log_warn "Could not verify TTL on blacklist keys"
            fi
        fi
    else
        log_info "No blacklist keys to verify TTL"
    fi
    
    # Test 3.3: Verify In-Memory Fallback Removed
    log_test "3.3: Verify in-memory blacklist fallback removed from auth_service.py"
    if grep -q "self.blacklisted_tokens: Set" /root/auth_service.py 2>/dev/null; then
        log_fail "In-memory blacklisted_tokens Set still exists in auth_service.py"
    else
        log_pass "In-memory blacklist fallback properly removed"
    fi
}

###############################################################################
# Test 4: Database Connection Pool Configuration
###############################################################################

test_connection_pool() {
    log_section "4. Database Connection Pool Configuration"
    
    # Test 4.1: Verify max_size Updated
    log_test "4.1: Verify connection pool max_size updated (should be 20 or 50)"
    MAX_SIZE=$(grep -A 2 "create_pool" /root/database.py | grep "max_size" | grep -oP '\d+' | head -1)
    if [ -z "$MAX_SIZE" ]; then
        log_fail "Could not find max_size in database.py"
    elif [ "$MAX_SIZE" -ge 20 ]; then
        log_pass "Connection pool max_size updated to $MAX_SIZE"
    else
        log_fail "Connection pool max_size is still $MAX_SIZE (should be 20+)"
    fi
    
    # Test 4.2: Verify min_size Updated
    log_test "4.2: Verify connection pool min_size updated (should be 5+)"
    MIN_SIZE=$(grep -A 2 "create_pool" /root/database.py | grep "min_size" | grep -oP '\d+' | head -1)
    if [ -z "$MIN_SIZE" ]; then
        log_fail "Could not find min_size in database.py"
    elif [ "$MIN_SIZE" -ge 5 ]; then
        log_pass "Connection pool min_size updated to $MIN_SIZE"
    else
        log_fail "Connection pool min_size is still $MIN_SIZE (should be 5+)"
    fi
    
    # Test 4.3: Verify command_timeout Reduced
    log_test "4.3: Verify command_timeout reduced to 30 seconds"
    TIMEOUT=$(grep -A 2 "create_pool" /root/database.py | grep "command_timeout" | grep -oP '\d+' | head -1)
    if [ -z "$TIMEOUT" ]; then
        log_warn "Could not find command_timeout in database.py"
    elif [ "$TIMEOUT" -le 30 ]; then
        log_pass "Command timeout set to $TIMEOUT seconds"
    else
        log_warn "Command timeout is $TIMEOUT seconds (recommended: 30)"
    fi
}

###############################################################################
# Test 5: AI Service Configuration
###############################################################################

test_ai_service() {
    log_section "5. AI Service Configuration"
    
    # Test 5.1: Verify AI Provider Configuration
    log_test "5.1: Verify AI_PROVIDER is properly configured"
    AI_PROVIDER=$(docker exec $BACKEND_CONTAINER printenv AI_PROVIDER 2>/dev/null || echo "")
    TOGETHER_KEY=$(docker exec $BACKEND_CONTAINER printenv TOGETHER_API_KEY 2>/dev/null || echo "")
    
    if [ "$AI_PROVIDER" == "together" ] && [ -z "$TOGETHER_KEY" ]; then
        log_fail "AI_PROVIDER=together but TOGETHER_API_KEY is empty!"
    elif [ "$AI_PROVIDER" == "sidecar" ]; then
        log_pass "AI_PROVIDER set to sidecar (no API key needed)"
    elif [ "$AI_PROVIDER" == "together" ] && [ -n "$TOGETHER_KEY" ]; then
        log_pass "AI_PROVIDER set to together with API key configured"
    else
        log_warn "AI_PROVIDER is '$AI_PROVIDER' (verify this is correct)"
    fi
    
    # Test 5.2: Check for Error Log Spam
    log_test "5.2: Verify no 'Together AI: API key not configured' errors in logs"
    ERROR_COUNT=$(docker logs $BACKEND_CONTAINER --tail 100 2>&1 | grep -c "Together AI: API key not configured" || echo "0")
    if [ "$ERROR_COUNT" -gt 5 ]; then
        log_fail "Found $ERROR_COUNT 'API key not configured' errors in recent logs"
    else
        log_pass "No excessive AI service errors in logs"
    fi
}

###############################################################################
# Test 6: Mailhog Service
###############################################################################

test_mailhog() {
    log_section "6. Mailhog Email Service"
    
    # Test 6.1: Verify Mailhog Container Running
    log_test "6.1: Verify mailhog container is running"
    if docker ps | grep -q "mailhog"; then
        log_pass "Mailhog container is running"
    else
        log_fail "Mailhog container is NOT running!"
    fi
    
    # Test 6.2: Verify SMTP Configuration
    log_test "6.2: Verify SMTP_HOST points to mailhog"
    SMTP_HOST=$(docker exec $BACKEND_CONTAINER printenv SMTP_HOST 2>/dev/null || echo "")
    if [ "$SMTP_HOST" == "mailhog" ]; then
        log_pass "SMTP_HOST correctly set to mailhog"
    else
        log_fail "SMTP_HOST is '$SMTP_HOST' (should be 'mailhog')"
    fi
    
    # Test 6.3: Verify Mailhog Web UI Accessible
    log_test "6.3: Verify Mailhog web UI is accessible"
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8025 | grep -q "200"; then
        log_pass "Mailhog web UI is accessible on port 8025"
    else
        log_warn "Mailhog web UI not accessible (may not be exposed)"
    fi
}

###############################################################################
# Test 7: OAuth Proxy Error Handling
###############################################################################

test_oauth_proxy() {
    log_section "7. OAuth Proxy Error Handling"
    
    # Test 7.1: Verify Null Check Added
    log_test "7.1: Verify null check added to oauthProxy.ts"
    if [ -f "/root/anwalts-frontend-new/server/utils/oauthProxy.ts" ]; then
        if grep -q "if (!rawSetCookie)" /root/anwalts-frontend-new/server/utils/oauthProxy.ts; then
            log_pass "Null check for rawSetCookie found in oauthProxy.ts"
        else
            log_fail "Null check for rawSetCookie NOT found in oauthProxy.ts"
        fi
    else
        log_warn "oauthProxy.ts not found at expected location"
    fi
    
    # Test 7.2: Verify Cookie Validation Loop
    log_test "7.2: Verify cookie validation added to loop"
    if [ -f "/root/anwalts-frontend-new/server/utils/oauthProxy.ts" ]; then
        if grep -q "cookie.trim().length > 0" /root/anwalts-frontend-new/server/utils/oauthProxy.ts; then
            log_pass "Cookie validation loop found in oauthProxy.ts"
        else
            log_fail "Cookie validation NOT found in oauthProxy.ts"
        fi
    else
        log_warn "oauthProxy.ts not found at expected location"
    fi
}

###############################################################################
# Test 8: Backup System
###############################################################################

test_backup_system() {
    log_section "8. Backup System Verification"
    
    # Test 8.1: Verify /backups Directory Exists
    log_test "8.1: Verify /backups directory exists with proper permissions"
    if [ -d "/backups" ]; then
        PERMS=$(stat -c "%a" /backups)
        if [ "$PERMS" == "700" ]; then
            log_pass "/backups directory exists with secure permissions (700)"
        else
            log_warn "/backups directory exists but permissions are $PERMS (should be 700)"
        fi
    else
        log_fail "/backups directory does NOT exist!"
    fi
    
    # Test 8.2: Verify Backup Script Exists
    log_test "8.2: Verify backup script exists and is executable"
    if [ -x "/root/scripts/backup-database.sh" ]; then
        log_pass "Backup script exists and is executable"
    elif [ -f "/root/scripts/backup-database.sh" ]; then
        log_fail "Backup script exists but is NOT executable"
    else
        log_fail "Backup script does NOT exist!"
    fi
    
    # Test 8.3: Verify Cron Job Scheduled
    log_test "8.3: Verify backup cron job is scheduled"
    if crontab -l 2>/dev/null | grep -q "backup-database.sh"; then
        CRON_SCHEDULE=$(crontab -l 2>/dev/null | grep "backup-database.sh")
        log_pass "Backup cron job is scheduled: $CRON_SCHEDULE"
    else
        log_fail "Backup cron job is NOT scheduled in crontab!"
    fi
    
    # Test 8.4: Check for Recent Backups
    log_test "8.4: Check for recent backup files"
    BACKUP_COUNT=$(find /backups -name "*.sql.gz" -mtime -7 2>/dev/null | wc -l || echo "0")
    if [ "$BACKUP_COUNT" -gt 0 ]; then
        log_pass "Found $BACKUP_COUNT backup(s) from last 7 days"
        LATEST=$(find /backups -name "*.sql.gz" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
        if [ -n "$LATEST" ]; then
            SIZE=$(du -h "$LATEST" 2>/dev/null | cut -f1)
            log_info "Latest backup: $LATEST ($SIZE)"
        fi
    else
        log_warn "No backups found from last 7 days (system may be new)"
    fi
}

###############################################################################
# Test 9: Monitoring Endpoints
###############################################################################

test_monitoring() {
    log_section "9. Monitoring and Observability"
    
    # Test 9.1: Verify /metrics or /health Endpoint
    log_test "9.1: Verify monitoring endpoint exists"
    HEALTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
    METRICS_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/metrics 2>/dev/null || echo "000")
    
    if [ "$HEALTH_CODE" == "200" ]; then
        log_pass "/health endpoint is accessible (HTTP 200)"
        HEALTH_RESPONSE=$(curl -s http://localhost:8000/health 2>/dev/null || echo "{}")
        log_info "Health response: $HEALTH_RESPONSE"
    elif [ "$METRICS_CODE" == "200" ]; then
        log_pass "/metrics endpoint is accessible (HTTP 200)"
    else
        log_warn "No monitoring endpoint found (/health or /metrics)"
    fi
    
    # Test 9.2: Check Container Health Status
    log_test "9.2: Verify all containers report healthy status"
    UNHEALTHY=$(docker ps --filter "health=unhealthy" --format "{{.Names}}" | wc -l)
    if [ "$UNHEALTHY" -gt 0 ]; then
        UNHEALTHY_LIST=$(docker ps --filter "health=unhealthy" --format "{{.Names}}")
        log_fail "$UNHEALTHY container(s) are unhealthy: $UNHEALTHY_LIST"
    else
        log_pass "All containers report healthy status"
    fi
}

###############################################################################
# Test 10: Container Health Checks
###############################################################################

test_container_health() {
    log_section "10. Container Health Status"
    
    CONTAINERS=("$BACKEND_CONTAINER" "$FRONTEND_CONTAINER" "$POSTGRES_CONTAINER" "$REDIS_CONTAINER")
    
    for CONTAINER in "${CONTAINERS[@]}"; do
        log_test "10.x: Verify $CONTAINER is running and healthy"
        STATUS=$(docker inspect --format='{{.State.Status}}' "$CONTAINER" 2>/dev/null || echo "not_found")
        HEALTH=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER" 2>/dev/null || echo "no_healthcheck")
        
        if [ "$STATUS" == "running" ]; then
            if [ "$HEALTH" == "healthy" ]; then
                log_pass "$CONTAINER is running and healthy"
            elif [ "$HEALTH" == "no_healthcheck" ]; then
                log_pass "$CONTAINER is running (no healthcheck defined)"
            else
                log_warn "$CONTAINER is running but health status is: $HEALTH"
            fi
        else
            log_fail "$CONTAINER status is: $STATUS"
        fi
    done
}

###############################################################################
# Test 11: Secret Security Validation
###############################################################################

test_secret_security() {
    log_section "11. Secret Security Validation"
    
    # Test 11.1: Verify GOOGLE_CLIENT_SECRET Not in Frontend
    log_test "11.1: Verify GOOGLE_CLIENT_SECRET not exposed in frontend"
    FRONTEND_SECRET=$(docker exec $FRONTEND_CONTAINER printenv GOOGLE_CLIENT_SECRET 2>/dev/null || echo "")
    if [ -z "$FRONTEND_SECRET" ]; then
        log_pass "GOOGLE_CLIENT_SECRET not exposed in frontend environment"
    else
        log_fail "GOOGLE_CLIENT_SECRET is EXPOSED in frontend environment!"
    fi
    
    # Test 11.2: Verify Secrets in Backend
    log_test "11.2: Verify critical secrets present in backend"
    BACKEND_HAS_GOOGLE_SECRET=$(docker exec $BACKEND_CONTAINER printenv GOOGLE_CLIENT_SECRET 2>/dev/null | wc -c)
    if [ "$BACKEND_HAS_GOOGLE_SECRET" -gt 10 ]; then
        log_pass "GOOGLE_CLIENT_SECRET properly configured in backend"
    else
        log_warn "GOOGLE_CLIENT_SECRET may not be configured in backend"
    fi
}

###############################################################################
# Final Report
###############################################################################

print_summary() {
    log_section "Test Summary"
    
    echo -e "${BLUE}Total Tests:${NC}  $TOTAL_TESTS"
    echo -e "${GREEN}Passed:${NC}       $PASSED_TESTS"
    echo -e "${RED}Failed:${NC}       $FAILED_TESTS"
    
    PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    
    echo ""
    if [ "$FAILED_TESTS" -eq 0 ]; then
        echo -e "${GREEN}✓ ALL TESTS PASSED! (100%)${NC}"
        echo -e "${GREEN}Security hardening implementation is complete and verified.${NC}"
        return 0
    elif [ "$PASS_RATE" -ge 80 ]; then
        echo -e "${YELLOW}⚠ MOSTLY PASSING ($PASS_RATE%)${NC}"
        echo -e "${YELLOW}Review failed tests above and fix issues.${NC}"
        return 1
    else
        echo -e "${RED}✗ MULTIPLE FAILURES ($PASS_RATE%)${NC}"
        echo -e "${RED}Critical issues detected. Review and fix before proceeding.${NC}"
        return 1
    fi
}

###############################################################################
# Main Execution
###############################################################################

main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║   Security Hardening Implementation Verification Test Suite       ║"
    echo "║   Version: 1.0                                                     ║"
    echo "║   Date: $(date +'%Y-%m-%d %H:%M:%S')                                          ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Check prerequisites
    log_info "Checking prerequisites..."
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}ERROR: docker is not installed or not in PATH${NC}"
        exit 1
    fi
    
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}ERROR: curl is not installed${NC}"
        exit 1
    fi
    
    # Run all test suites
    test_secret_rotation
    test_network_security
    test_redis_blacklist
    test_connection_pool
    test_ai_service
    test_mailhog
    test_oauth_proxy
    test_backup_system
    test_monitoring
    test_container_health
    test_secret_security
    
    # Print summary and exit
    print_summary
    exit $?
}

# Run main function
main "$@"
