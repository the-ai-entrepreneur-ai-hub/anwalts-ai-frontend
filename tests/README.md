# Security Hardening Verification Tests

Comprehensive test suite to verify security hardening implementation.

## Quick Start

```bash
cd /root/tests
chmod +x *.sh
./run_all_tests.sh
```

## Test Files

| File | Description | Type |
|------|-------------|------|
| `run_all_tests.sh` | Master test runner | Bash |
| `security_hardening_verification.sh` | Main verification (70+ tests) | Bash |
| `test_redis_blacklist.py` | Redis blacklist unit tests | Python/pytest |
| `test_connection_pool_load.py` | Connection pool load tests | Python/asyncio |
| `test_oauth_proxy_errors.py` | OAuth error handling tests | Python/requests |
| `TEST_DOCUMENTATION.md` | Complete test documentation | Markdown |

## Usage

### Run All Tests (Recommended)
```bash
./run_all_tests.sh --full
```

### Quick Tests Only (5 minutes)
```bash
./run_all_tests.sh --quick
```

### Individual Test Suites
```bash
# Master verification (most important)
./security_hardening_verification.sh

# Redis blacklist tests
pytest test_redis_blacklist.py -v

# Connection pool load tests
python3 test_connection_pool_load.py

# OAuth proxy tests
python3 test_oauth_proxy_errors.py
```

## Requirements

- Docker (running)
- Python 3.8+
- curl, nc (netcat)
- Optional: pytest, asyncpg, redis, requests

Install Python dependencies:
```bash
pip3 install pytest asyncpg redis requests
```

## Expected Results

- **100% pass**: Ready for production ✅
- **90-99% pass**: Review failures, fix minor issues ⚠️
- **80-89% pass**: Multiple issues, fix before production ⚠️
- **<80% pass**: Critical issues, DO NOT deploy ❌

## Documentation

See `TEST_DOCUMENTATION.md` for detailed test coverage, troubleshooting, and CI/CD integration.

## Support

Questions? Check:
1. `TEST_DOCUMENTATION.md` for detailed guides
2. `../CRITIQUE_SUMMARY.md` for known issues
3. `../design.md` for architecture details

