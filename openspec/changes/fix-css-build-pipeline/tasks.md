# Implementation Tasks

## 1. Stage 1 - Critical Fixes (P0)
- [x] 1.1 Update Dockerfile with multi-stage build
- [x] 1.2 Add spacing configuration to tailwind.config.ts
- [x] 1.3 Update tailwind.css with @theme block for Tailwind v4
- [x] 1.4 Clean up main.css (remove .gap-12 utility)
- [x] 1.5 Test build locally
- [x] 1.6 Rebuild Docker image
- [x] 1.7 Deploy and verify

## 2. Stage 2 - Build Validation (P1, Optional)
- [ ] 2.1 Create scripts/validate-build.js
- [ ] 2.2 Update package.json with build:validate script
- [ ] 2.3 Test validation script
- [ ] 2.4 Document validation process

## 3. Testing & Verification
- [x] 3.1 Verify Dockerfile builds successfully
- [x] 3.2 Verify CSS files generated in .output
- [x] 3.3 Verify Tailwind utilities present in CSS
- [x] 3.4 Verify --spacing CSS variable defined in @theme
- [x] 3.5 Test dashboard card spacing visually
- [x] 3.6 Test Settings page form styling
- [x] 3.7 Check browser console for CSS errors
- [x] 3.8 Verify page load time acceptable

## 4. Deployment
- [x] 4.1 Build Docker image: `docker-compose build --no-cache frontend`
- [x] 4.2 Stop frontend container: `docker-compose down frontend`
- [x] 4.3 Start frontend container: `docker-compose up -d frontend`
- [x] 4.4 Restart nginx: `docker restart anwalts_nginx`
- [x] 4.5 Wait for health check (30 seconds)
- [x] 4.6 Smoke test dashboard page
- [x] 4.7 Monitor logs for errors

## 5. Documentation
- [x] 5.1 Update deployment documentation
- [x] 5.2 Document new build process
- [x] 5.3 Add troubleshooting guide
- [x] 5.4 Mark proposal as completed

## Notes
- **Completed**: 2025-11-03
- **Actual time**: ~2 hours (including troubleshooting Tailwind v4 behavior)
- **Key learning**: Tailwind v4 uses CSS variables by default, requires @theme block
- **Rollback**: Backup image tagged as `root_frontend:backup-before-css-fix`
