#!/bin/bash

# ANWALTS.AI Frontend Startup Script
# This script sets environment variables and starts the Nuxt server

set -e

echo "🚀 Starting ANWALTS.AI Frontend..."

# Set environment variables (update these as needed)
export NODE_ENV="${NODE_ENV:-production}"
if [ -z "${GOOGLE_CLIENT_ID}" ]; then
  echo "[start.sh] GOOGLE_CLIENT_ID is not set. Please export it before running this script." >&2
  exit 1
fi

if [ -z "${GOOGLE_CLIENT_SECRET}" ]; then
  echo "[start.sh] GOOGLE_CLIENT_SECRET is not set. Please export it before running this script." >&2
  exit 1
fi

export GOOGLE_CLIENT_ID
export GOOGLE_CLIENT_SECRET
export GOOGLE_REDIRECT_URI="${GOOGLE_REDIRECT_URI:-https://portal-anwalts.ai/api/auth/oauth/google/callback}"
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
