#!/bin/bash
set -e

echo "================================"
echo "ANWALTS.AI Authentication Tests"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check Database User
echo "Test 1: Verify test user in database..."
USER_EXISTS=$(docker exec fa8ba6a7716d_anwalts_postgres psql -U anwalts_user -d anwalts_ai -tAc "SELECT COUNT(*) FROM users WHERE email = 'test@anwalts.ai';")
if [ "$USER_EXISTS" = "1" ]; then
    echo -e "${GREEN}✓${NC} Test user exists in database"
else
    echo -e "${RED}✗${NC} Test user not found!"
    exit 1
fi

# Test 2: Backend Health
echo ""
echo "Test 2: Check backend health..."
HEALTH=$(curl -s http://localhost:8000/health | grep -o '"status":"healthy"' || echo "")
if [ -n "$HEALTH" ]; then
    echo -e "${GREEN}✓${NC} Backend is healthy"
else
    echo -e "${RED}✗${NC} Backend health check failed!"
    exit 1
fi

# Test 3: Login API
echo ""
echo "Test 3: Test login endpoint..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@anwalts.ai", "password": "Test1234"}')

SUCCESS=$(echo "$LOGIN_RESPONSE" | grep -o '"success":true' || echo "")
if [ -n "$SUCCESS" ]; then
    echo -e "${GREEN}✓${NC} Login API works correctly"
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    echo -e "${YELLOW}   Token:${NC} ${TOKEN:0:50}..."
else
    echo -e "${RED}✗${NC} Login failed!"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

# Test 4: OAuth Redirect URI
echo ""
echo "Test 4: Verify OAuth configuration..."
REDIRECT_URI=$(docker exec anwalts_backend printenv GOOGLE_REDIRECT_URI)
if [ "$REDIRECT_URI" = "https://portal-anwalts.ai/api/auth/google/callback" ]; then
    echo -e "${GREEN}✓${NC} OAuth redirect URI is correct"
else
    echo -e "${RED}✗${NC} OAuth redirect URI mismatch!"
    echo "   Current: $REDIRECT_URI"
    echo "   Expected: https://portal-anwalts.ai/api/auth/google/callback"
    exit 1
fi

# Test 5: Frontend Health
echo ""
echo "Test 5: Check frontend health..."
FRONTEND_STATUS=$(docker inspect anwalts_frontend --format='{{.State.Health.Status}}')
if [ "$FRONTEND_STATUS" = "healthy" ]; then
    echo -e "${GREEN}✓${NC} Frontend is healthy"
else
    echo -e "${YELLOW}⚠${NC}  Frontend status: $FRONTEND_STATUS"
fi

# Summary
echo ""
echo "================================"
echo -e "${GREEN}All authentication tests passed!${NC}"
echo "================================"
echo ""
echo "📋 Next Steps:"
echo "   1. Navigate to: https://portal-anwalts.ai/"
echo "   2. Click 'Login with Google'"
echo "   3. Complete OAuth flow"
echo "   4. Verify you stay on /dashboard"
echo ""
echo "🔑 Manual Test Credentials:"
echo "   Email: test@anwalts.ai"
echo "   Password: Test1234"
echo ""
echo "📊 Service URLs:"
echo "   Frontend: https://portal-anwalts.ai/"
echo "   Backend: http://localhost:8000/"
echo "   Backend API Docs: http://localhost:8000/docs"
echo ""
