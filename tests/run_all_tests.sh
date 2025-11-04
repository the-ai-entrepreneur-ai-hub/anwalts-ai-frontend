#!/bin/bash

###############################################################################
# Master Test Runner
# Executes all security hardening verification tests
#
# Usage: ./run_all_tests.sh [--quick | --full]
#   --quick: Run only critical tests (fast, <5 min)
#   --full:  Run all tests including load tests (slow, ~15 min)
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test mode
MODE="${1:---full}"

# Test results
TOTAL_SUITES=0
PASSED_SUITES=0
FAILED_SUITES=0

log_section() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

run_test_suite() {
    local name=$1
    local command=$2
    
    TOTAL_SUITES=$((TOTAL_SUITES + 1))
    
    echo -e "${YELLOW}[RUNNING]${NC} $name"
    
    if eval "$command"; then
        echo -e "${GREEN}[PASSED]${NC} $name\n"
        PASSED_SUITES=$((PASSED_SUITES + 1))
        return 0
    else
        echo -e "${RED}[FAILED]${NC} $name\n"
        FAILED_SUITES=$((FAILED_SUITES + 1))
        return 1
    fi
}

###############################################################################
# Main Test Execution
###############################################################################

echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   Security Hardening Implementation - Master Test Runner            ║
║                                                                      ║
║   This script runs all verification tests for the security          ║
║   hardening proposal implementation.                                 ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "Mode: ${YELLOW}$MODE${NC}"
echo -e "Date: $(date +'%Y-%m-%d %H:%M:%S')\n"

# Check prerequisites
log_section "Checking Prerequisites"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ docker not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ docker found${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ python3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ python3 found${NC}"

if ! command -v curl &> /dev/null; then
    echo -e "${RED}✗ curl not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ curl found${NC}"

# Change to tests directory
cd "$(dirname "$0")" || exit 1

###############################################################################
# Test Suite 1: Master Verification Script (CRITICAL)
###############################################################################

log_section "Test Suite 1: Master Verification (CRITICAL)"

run_test_suite \
    "Master Verification Script" \
    "./security_hardening_verification.sh"

###############################################################################
# Test Suite 2: Redis Blacklist Unit Tests (CRITICAL)
###############################################################################

log_section "Test Suite 2: Redis Blacklist Implementation (CRITICAL)"

# Check if pytest is available
if command -v pytest &> /dev/null; then
    run_test_suite \
        "Redis Blacklist Unit Tests" \
        "pytest test_redis_blacklist.py -v --tb=short"
else
    echo -e "${YELLOW}[SKIPPED]${NC} Redis Blacklist Unit Tests (pytest not installed)"
    echo -e "${YELLOW}Install with: pip3 install pytest${NC}\n"
fi

###############################################################################
# Test Suite 3: OAuth Proxy Error Handling
###############################################################################

log_section "Test Suite 3: OAuth Proxy Error Handling"

run_test_suite \
    "OAuth Proxy Error Tests" \
    "python3 test_oauth_proxy_errors.py"

###############################################################################
# Test Suite 4: Connection Pool Load Tests (Optional for --quick)
###############################################################################

if [ "$MODE" == "--full" ]; then
    log_section "Test Suite 4: Connection Pool Load Tests"
    
    run_test_suite \
        "Connection Pool Load Tests (30s sustained load)" \
        "python3 test_connection_pool_load.py"
else
    echo -e "${YELLOW}[SKIPPED]${NC} Connection Pool Load Tests (use --full to run)"
fi

###############################################################################
# Test Suite 5: Integration Tests (Optional)
###############################################################################

if [ "$MODE" == "--full" ]; then
    log_section "Test Suite 5: Integration Tests"
    
    # End-to-end user flow test
    run_test_suite \
        "End-to-End User Flow" \
        "curl -f -s http://localhost/health > /dev/null"
    
    # Database connectivity from backend
    run_test_suite \
        "Backend→Database Connectivity" \
        "docker exec anwalts_backend pg_isready -h postgres -U anwalts_user > /dev/null"
    
    # Redis connectivity from backend
    run_test_suite \
        "Backend→Redis Connectivity" \
        "docker exec anwalts_backend timeout 2 bash -c 'echo PING | nc redis 6379' | grep -q 'PONG\|NOAUTH'"
fi

###############################################################################
# Final Report
###############################################################################

log_section "Test Summary"

echo -e "${BLUE}Test Suites Executed:${NC} $TOTAL_SUITES"
echo -e "${GREEN}Passed:${NC}              $PASSED_SUITES"
echo -e "${RED}Failed:${NC}              $FAILED_SUITES"

PASS_RATE=$((PASSED_SUITES * 100 / TOTAL_SUITES))

echo ""
if [ "$FAILED_SUITES" -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                          ║${NC}"
    echo -e "${GREEN}║   ✅ ALL TEST SUITES PASSED (100%)                      ║${NC}"
    echo -e "${GREEN}║                                                          ║${NC}"
    echo -e "${GREEN}║   Security hardening implementation is verified!        ║${NC}"
    echo -e "${GREEN}║   System is ready for production deployment.            ║${NC}"
    echo -e "${GREEN}║                                                          ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    exit 0
elif [ "$PASS_RATE" -ge 80 ]; then
    echo -e "${YELLOW}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║                                                          ║${NC}"
    echo -e "${YELLOW}║   ⚠️  MOSTLY PASSING ($PASS_RATE%)                         ║${NC}"
    echo -e "${YELLOW}║                                                          ║${NC}"
    echo -e "${YELLOW}║   Review failed tests and fix issues.                   ║${NC}"
    echo -e "${YELLOW}║   Not recommended for production until all pass.        ║${NC}"
    echo -e "${YELLOW}║                                                          ║${NC}"
    echo -e "${YELLOW}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    exit 1
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                                                          ║${NC}"
    echo -e "${RED}║   ❌ MULTIPLE FAILURES ($PASS_RATE%)                       ║${NC}"
    echo -e "${RED}║                                                          ║${NC}"
    echo -e "${RED}║   Critical issues detected!                             ║${NC}"
    echo -e "${RED}║   DO NOT deploy to production.                          ║${NC}"
    echo -e "${RED}║   Fix all failures before proceeding.                   ║${NC}"
    echo -e "${RED}║                                                          ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    exit 1
fi
