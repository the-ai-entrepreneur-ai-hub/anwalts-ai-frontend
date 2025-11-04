#!/bin/bash

echo "=== Testing Google OAuth Flow ==="
echo ""

# Test 1: Check if backend is running
echo "1. Testing backend availability..."
curl -s http://localhost:8000/docs | grep -q "AnwaltsAI" && echo "✓ Backend API is running" || echo "✗ Backend API is not accessible"

# Test 2: Check if frontend is running
echo ""
echo "2. Testing frontend availability..."
curl -s http://localhost:3000 | grep -q "<!DOCTYPE html>" && echo "✓ Frontend is running" || echo "✗ Frontend is not accessible"

# Test 3: Test OAuth callback endpoint
echo ""
echo "3. Testing OAuth callback endpoint..."
response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000/api/auth/google/callback?code=test")
if [ "$response" = "302" ] || [ "$response" = "301" ]; then
    echo "✓ OAuth callback endpoint is responding with redirect (expected)"
else
    echo "✗ OAuth callback endpoint returned: $response"
fi

# Test 4: Test OAuth initiation endpoint
echo ""
echo "4. Testing OAuth initiation endpoint..."
response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000/api/auth/google")
if [ "$response" = "302" ] || [ "$response" = "301" ]; then
    echo "✓ OAuth initiation endpoint is responding with redirect (expected)"
else
    echo "✗ OAuth initiation endpoint returned: $response"
fi

# Test 5: Check nginx status
echo ""
echo "5. Checking nginx status..."
systemctl is-active nginx >/dev/null 2>&1 && echo "✓ Nginx is running" || echo "✗ Nginx is not running"

# Test 6: Test production endpoint
echo ""
echo "6. Testing production endpoint (if accessible)..."
response=$(curl -s -o /dev/null -w "%{http_code}" "https://portal-anwalts.ai/api/auth/google/callback?code=test" --max-time 5 2>/dev/null)
if [ "$response" = "302" ] || [ "$response" = "301" ] || [ "$response" = "200" ]; then
    echo "✓ Production OAuth endpoint is accessible"
else
    echo "ℹ Production endpoint returned: $response (may need HTTPS setup)"
fi

echo ""
echo "=== OAuth Flow Test Complete ==="
echo ""
echo "Next steps to test the full flow:"
echo "1. Open https://portal-anwalts.ai in a browser"
echo "2. Click on 'Sign in with Google' button"
echo "3. Complete Google authentication"
echo "4. Verify redirect to dashboard"
