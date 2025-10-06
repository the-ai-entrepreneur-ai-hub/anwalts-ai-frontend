#!/bin/bash

# ANWALTS.AI Frontend Startup Script
# This script sets environment variables and starts the Nuxt server

set -e

echo "🚀 Starting ANWALTS.AI Frontend..."

# Set environment variables (update these as needed)
export NODE_ENV="${NODE_ENV:-production}"
export GOOGLE_CLIENT_ID="${GOOGLE_CLIENT_ID:-116750545961-k22ajbftbikioa14rk2jhr7b04lm6am2.apps.googleusercontent.com}"
export GOOGLE_CLIENT_SECRET="${GOOGLE_CLIENT_SECRET:-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}"
# Default to the Nuxt/Supabase callback that actually exists; override in env if backend handles Google callback
export GOOGLE_REDIRECT_URI="${GOOGLE_REDIRECT_URI:-https://portal-anwalts.ai/api/auth/google/callback}"
export BACKEND_BASE="${BACKEND_BASE:-http://backend_api:8000}"

echo "✓ Environment variables set"
echo "  - NODE_ENV: ${NODE_ENV}"
echo "  - GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID:0:20}..."
echo "  - GOOGLE_REDIRECT_URI: ${GOOGLE_REDIRECT_URI}"
echo "  - BACKEND_BASE: ${BACKEND_BASE}"

# Check if build exists
if [ ! -f ".output/server/index.mjs" ]; then
  echo "❌ Build not found. Please run 'npm run build' first."
  exit 1
fi

echo "✓ Build found"

# Start the server
echo "🌐 Starting Nuxt server..."
node .output/server/index.mjs
