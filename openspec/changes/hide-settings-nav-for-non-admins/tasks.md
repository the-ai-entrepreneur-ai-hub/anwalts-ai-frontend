## Implementation Tasks

### 1. Update PortalShell Component
- [x] 1.1 Import `useAuth` composable in `PortalShell.vue` script section
- [x] 1.2 Destructure `isAdmin` from `useAuth()` call
- [x] 1.3 Add `v-if="isAdmin"` directive to Settings navigation link (line 67)
- [ ] 1.4 Verify no TypeScript errors or linting issues

### 2. Build and Deploy
- [ ] 2.1 Run `npm run build` in `/root/anwalts-frontend-new`
- [ ] 2.2 Verify build completes successfully
- [ ] 2.3 Build Docker image: `docker build -t anwalts-frontend -f Dockerfile .`
- [ ] 2.4 Stop and remove old container
- [ ] 2.5 Start new container with updated image
- [ ] 2.6 Verify container is running and healthy

### 3. Testing
- [ ] 3.1 Test as admin user (test.reg.e2e+20251026@anwalts.ai)
  - [ ] 3.1.1 Login and verify Settings tab is visible
  - [ ] 3.1.2 Click Settings tab and verify access works
  - [ ] 3.1.3 Verify all settings functionality works
  
- [ ] 3.2 Test as admin user (angelageneralao.1997@gmail.com)
  - [ ] 3.2.1 Login and verify Settings tab is visible
  - [ ] 3.2.2 Verify access works
  
- [ ] 3.3 Test as non-admin user (any other email)
  - [ ] 3.3.1 Login and verify Settings tab is NOT visible
  - [ ] 3.3.2 Verify other navigation tabs work (Dashboard, Assistant, Documents, etc.)
  - [ ] 3.3.3 Navigate to `/settings` directly via URL
  - [ ] 3.3.4 Verify "Access Denied" message still appears (defense-in-depth)
  
- [ ] 3.4 Test edge cases
  - [ ] 3.4.1 Test with uppercase/lowercase email variations
  - [ ] 3.4.2 Test mobile responsive layout
  - [ ] 3.4.3 Verify no console errors or warnings

### 4. Documentation
- [ ] 4.1 Update DEPLOYMENT_COMPLETE document if needed
- [ ] 4.2 Document the change in implementation notes

### 5. Archive
- [ ] 5.1 After successful deployment and testing, archive this change
- [ ] 5.2 Run `openspec archive hide-settings-nav-for-non-admins --yes`
