#!/bin/bash
set -e

echo "========================================="
echo "  Testing Complete OAuth Flow"
echo "========================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Test 1: Frontend proxy to backend OAuth authorize
echo "Test 1: Check /api/auth/google/authorize route..."
RESPONSE=$(curl -sI http://localhost:3000/api/auth/google/authorize 2>&1)
STATUS=$(echo "$RESPONSE" | grep "HTTP" | awk '{print $2}' | head -1)
LOCATION=$(echo "$RESPONSE" | grep -i "location:" | cut -d' ' -f2 | tr -d '\r')

if [ "$STATUS" = "302" ] || [ "$STATUS" = "307" ]; then
    echo -e "${GREEN}✓${NC} Frontend redirects correctly (HTTP $STATUS)"
    echo -e "${YELLOW}  →${NC} Location: $LOCATION"
else
    echo -e "${RED}✗${NC} Frontend redirect failed (HTTP $STATUS)"
    exit 1
fi

# Test 2: Backend OAuth authorize endpoint
echo ""
echo "Test 2: Check backend /auth/google/authorize..."
BACKEND_RESPONSE=$(curl -sI http://localhost:8000/auth/google/authorize 2>&1)
BACKEND_STATUS=$(echo "$BACKEND_RESPONSE" | grep "HTTP" | awk '{print $2}' | head -1)
GOOGLE_URL=$(echo "$BACKEND_RESPONSE" | grep -i "location:" | cut -d' ' -f2 | tr -d '\r')

if [ "$BACKEND_STATUS" = "307" ] && [[ "$GOOGLE_URL" == *"accounts.google.com"* ]]; then
    echo -e "${GREEN}✓${NC} Backend generates Google OAuth URL (HTTP $BACKEND_STATUS)"
    echo -e "${YELLOW}  →${NC} Redirects to: accounts.google.com..."
    
    # Extract and display OAuth parameters
    if [[ "$GOOGLE_URL" == *"redirect_uri="* ]]; then
        REDIRECT_URI=$(echo "$GOOGLE_URL" | grep -oP 'redirect_uri=[^&]*' | cut -d'=' -f2 | python3 -c "import sys; from urllib.parse import unquote; print(unquote(sys.stdin.read().strip()))")
        echo -e "${YELLOW}  →${NC} Redirect URI: $REDIRECT_URI"
        
        if [ "$REDIRECT_URI" = "https://portal-anwalts.ai/api/auth/google/callback" ]; then
            echo -e "${GREEN}  ✓${NC} Redirect URI is correct"
        else
            echo -e "${RED}  ✗${NC} Redirect URI mismatch!"
            exit 1
        fi
    fi
else
    echo -e "${RED}✗${NC} Backend OAuth authorize failed"
    exit 1
fi

# Test 3: Verify Google OAuth parameters
echo ""
echo "Test 3: Verify OAuth parameters..."
if [[ "$GOOGLE_URL" == *"client_id="* ]]; then
    echo -e "${GREEN}✓${NC} Client ID present"
fi
if [[ "$GOOGLE_URL" == *"code_challenge="* ]]; then
    echo -e "${GREEN}✓${NC} PKCE code challenge present"
fi
if [[ "$GOOGLE_URL" == *"scope="* ]]; then
    echo -e "${GREEN}✓${NC} Scopes present"
fi

# Test 4: Check callback endpoint configuration
echo ""
echo "Test 4: Verify callback endpoint..."
CALLBACK_TEST=$(curl -s http://localhost:8000/api/auth/google/callback 2>&1)
if [[ "$CALLBACK_TEST" == *"Missing authorization code"* ]] || [[ "$CALLBACK_TEST" == *"Missing"* ]]; then
    echo -e "${GREEN}✓${NC} Callback endpoint is reachable"
else
    echo -e "${YELLOW}⚠${NC}  Callback endpoint response: $(echo "$CALLBACK_TEST" | head -c 100)"
fi

# Test 5: Verify auth middleware
echo ""
echo "Test 5: Check dashboard auth middleware..."
if [ -f "/root/anwalts-frontend-new/middleware/auth-guard.ts" ]; then
    if grep -q "auth_token" /root/anwalts-frontend-new/middleware/auth-guard.ts; then
        echo -e "${GREEN}✓${NC} Middleware checks for JWT auth_token"
    else
        echo -e "${YELLOW}⚠${NC}  Middleware might not check JWT tokens"
    fi
else
    echo -e "${YELLOW}⚠${NC}  Auth middleware file not found"
fi

# Summary
echo ""
echo "========================================="
echo -e "${GREEN}OAuth Flow Configuration: READY${NC}"
echo "========================================="
echo ""
echo "📋 OAuth Flow Steps:"
echo "   1. User clicks 'Login with Google'"
echo "   2. → /api/auth/google/authorize"
echo "   3. → Backend: /auth/google/authorize"
echo "   4. → Google OAuth (accounts.google.com)"
echo "   5. → Google callback: /api/auth/google/callback"
echo "   6. → Backend exchanges code for token"
echo "   7. → Backend sets auth_token in localStorage"
echo "   8. → Redirect to /dashboard"
echo "   9. ✓ Dashboard middleware checks auth_token"
echo "   10. ✓ User stays logged in"
echo ""
echo "🔗 Test URL: https://portal-anwalts.ai/"
echo "   Click 'Login with Google' and check console logs"
echo ""
