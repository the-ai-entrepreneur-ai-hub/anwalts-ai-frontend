#!/bin/bash

echo "🔍 ANWALTS.AI Frontend - Build Verification"
echo "==========================================="
echo ""

# Check public directory
echo "✓ Checking public directory..."
if [ -d "public" ]; then
  echo "  ✅ public/ exists"
  echo "  Files:"
  ls -lh public/
  if [ -d "public/shared" ]; then
    echo "  ✅ public/shared/ exists"
    echo "  Shared files:"
    ls -lh public/shared/
  fi
else
  echo "  ❌ public/ directory not found"
fi

echo ""

# Check build output
echo "✓ Checking build output..."
if [ -f ".output/server/index.mjs" ]; then
  echo "  ✅ Server bundle exists"
else
  echo "  ❌ Server bundle not found - run 'npm run build'"
fi

if [ -d ".output/server/chunks/routes/auth" ]; then
  echo "  ✅ OAuth routes built"
  ls -lh .output/server/chunks/routes/auth/
  if [ -d ".output/server/chunks/routes/auth/google" ]; then
    echo "  ✅ Google OAuth route built"
    ls -lh .output/server/chunks/routes/auth/google/
  fi
else
  echo "  ❌ OAuth routes not found"
fi

echo ""

# Check environment variables
echo "✓ Checking environment variables..."
if [ -n "$GOOGLE_CLIENT_ID" ]; then
  echo "  ✅ GOOGLE_CLIENT_ID is set"
else
  echo "  ⚠️  GOOGLE_CLIENT_ID not set"
fi

if [ -n "$BACKEND_BASE" ]; then
  echo "  ✅ BACKEND_BASE is set: $BACKEND_BASE"
else
  echo "  ⚠️  BACKEND_BASE not set"
fi

echo ""

# Summary
echo "==========================================="
echo "Build verification complete!"
echo ""
echo "Next steps:"
echo "1. Set environment variables (if not set)"
echo "2. Run ./start.sh to start the server"
echo "3. Visit http://localhost:3000 to test"
echo ""
