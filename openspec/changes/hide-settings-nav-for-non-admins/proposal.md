# Hide Settings Navigation for Non-Admin Users

## Why

Currently, the Settings navigation tab in the sidebar is visible to all authenticated users, but when non-admin users click it, they see an "Access Denied" message. This creates a poor user experience where users are shown options they cannot access.

**Problem:**
- Users see a Settings tab they cannot use
- Creates confusion and frustration when access is denied
- Violates principle of "don't show what users can't access"
- Current implementation shows the tab to all users (line 67 in `PortalShell.vue`)
- Access control happens at page level (lines 24-28 in `settings.vue`), not navigation level

**Better approach:**
- Hide the Settings tab entirely for non-admin users
- Only admins should see the navigation option
- Prevents confusion and improves UX
- Maintains security at both navigation and page levels

## What Changes

- **Modify `PortalShell.vue`**: Add conditional rendering to Settings navigation link based on admin status
- **Use existing `useAuth()` composable**: Leverage the existing `isAdmin` computed property
- **Maintain page-level security**: Keep existing access control in `settings.vue` as defense-in-depth
- **No changes to admin list**: Continue using hardcoded admin emails (test.reg.e2e+20251026@anwalts.ai, angelageneralao.1997@gmail.com)

### Files Modified
- `anwalts-frontend-new/components/PortalShell.vue` - Add conditional rendering for Settings link

### Admin Users (unchanged)
- `test.reg.e2e+20251026@anwalts.ai` (test email)
- `angelageneralao.1997@gmail.com` (Hangella)

## Impact

### User Experience
- **Non-admin users**: Settings tab disappears from navigation, cleaner interface
- **Admin users**: No change, Settings tab remains visible and accessible

### Technical Impact
- **Affected component**: `PortalShell.vue` (navigation component used across all protected pages)
- **Affected pages**: None directly, only navigation visibility changes
- **Security**: Defense-in-depth maintained (navigation visibility + page-level access control)
- **Testing**: Manual testing required with admin and non-admin accounts

### Breaking Changes
None. This is a UI enhancement that improves existing access control.

### Backwards Compatibility
Fully compatible. Existing admin users retain full access, non-admins simply don't see the option anymore.
