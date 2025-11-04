# ============================================
# Stage 1: BUILD
# ============================================
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies including devDependencies for build
COPY package*.json ./
RUN npm ci

# Copy source files
COPY . .

# Build the application (generates .output with proper CSS)
RUN npm run build

# ============================================
# Stage 2: PRODUCTION RUNTIME
# ============================================
FROM node:20-alpine

WORKDIR /app

# Copy only production dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy built output from builder stage
COPY --from=builder /app/.output ./.output
COPY --from=builder /app/public ./public

# Set environment variables
ENV NODE_ENV=production
ENV NITRO_HOST=0.0.0.0
ENV NITRO_PORT=3000

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start the application
CMD ["node", ".output/server/index.mjs"]