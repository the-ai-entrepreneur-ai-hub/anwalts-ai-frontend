# OAuth secrets should be set as environment variables
# export GOOGLE_CLIENT_ID=your_google_client_id_here
# export GOOGLE_CLIENT_SECRET=your_google_client_secret_here
export GOOGLE_REDIRECT_URI=https://portal-anwalts.ai/api/auth/google/callback
export NODE_ENV=production
export NITRO_PORT=3000
export NITRO_HOST=0.0.0.0

# Kill any existing Node.js server
pkill -f 'node.*index.mjs' 2>/dev/null

# Start the server
exec node .output/server/index.mjs
