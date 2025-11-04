# Admin-Only Settings Dashboard Setup

## Overview
The admin-only settings dashboard provides authorized administrators with access to system statistics, organization configuration, and administrative controls.

## Authorized Admin Emails
The following email addresses have admin access:
- `test.reg.e2e+20251026@anwalts.ai`
- `angelageneralao.1997@gmail.com`

## Configuration

### Environment Variables
The admin emails are configured in two locations for defense-in-depth security:

1. **Hardcoded in `backend-main.py` (line ~1201)**:
   ```python
   AUTHORIZED_ADMINS = {
       "test.reg.e2e+20251026@anwalts.ai",
       "angelageneralao.1997@gmail.com"
   }
   ```

2. **Environment variable in `docker-compose.yml`**:
   ```yaml
   - ADMIN_EMAILS=test.reg.e2e+20251026@anwalts.ai,angelageneralao.1997@gmail.com
   ```

### Database Setup
Admin users must have their role set to 'admin' in the database:

```sql
-- Set admin roles for authorized emails
UPDATE users 
SET role = 'admin' 
WHERE LOWER(email) IN (
  'test.reg.e2e+20251026@anwalts.ai',
  'angelageneralao.1997@gmail.com'
);

-- Verify admin roles
SELECT id, email, role FROM users WHERE role = 'admin';
```

Migration script available at: `/root/migrations/set_admin_roles.sql`

## Access Control

### Three-Layer Security
1. **Frontend Guard** (`useAuth()` composable):
   - Checks email against authorized admin list
   - Redirects non-admins to /dashboard
   - Shows "Access Denied" message

2. **Backend Middleware** (lines 606-621 in `backend-main.py`):
   - Blocks all `/api/admin/*` requests from non-admins
   - Returns 403 Forbidden before reaching endpoint

3. **API Endpoint** (each admin endpoint):
   - Calls `_assert_admin(current_user)` for explicit verification
   - Raises HTTPException(403) for non-admins

## Features

### System Statistics
- Active users count
- Connected email accounts
- Total documents
- Total templates
- Active API tokens
- Active webhooks

### Organization Settings
- **General**: Language, timezone
- **Security**: Two-factor auth, SSO, password requirements
- **Notifications**: Email, browser, AI updates
- **AI Configuration**: Model selection, creativity level, auto-save

### Administrative Links
- User management (/dashboard/settings/users)
- API token management (/dashboard/settings/api)
- Webhook management (/dashboard/settings/webhooks)

### Recent Activity
- Last 7 days of system events
- Grouped by event type with counts
- Shows last occurrence timestamp

## API Endpoints

### GET /api/admin/settings
Returns comprehensive admin settings data.

**Authorization**: Requires admin role

**Response**:
```json
{
  "organization": { ...organization_settings... },
  "statistics": {
    "active_users": 42,
    "connected_emails": 18,
    "total_documents": 1337,
    "total_templates": 56,
    "active_tokens": 3,
    "active_webhooks": 2
  },
  "recent_activity": [...],
  "current_user": {
    "id": "...",
    "email": "test.reg.e2e+20251026@anwalts.ai",
    "role": "admin"
  }
}
```

### PUT /api/admin/settings/organization
Updates organization settings.

**Authorization**: Requires admin role

**Request**:
```json
{
  "language": "en",
  "timezone": "Europe/Vienna",
  "require_two_factor": true,
  "ai_creativity": 80
}
```

**Allowed Fields**:
- language, timezone
- require_two_factor, enable_sso
- password_min_length, password_require_special, password_require_numbers
- email_notifications, browser_notifications, ai_updates
- ai_model, ai_creativity, auto_save

## Deployment

### Initial Setup
1. Update `docker-compose.yml` with ADMIN_EMAILS (already done)
2. Run database migration:
   ```bash
   docker exec -i anwalts_postgres psql -U anwalts_user -d anwalts_ai < /root/migrations/set_admin_roles.sql
   ```

### Restart Services
```bash
# Restart backend to pick up code changes
docker restart anwalts_backend

# Restart frontend if modified
docker restart anwalts_frontend

# Reload nginx
docker exec anwalts_nginx nginx -s reload
```

### Verify Deployment
1. Login as admin user: test.reg.e2e+20251026@anwalts.ai
2. Navigate to https://portal-anwalts.ai/dashboard/settings
3. Verify full admin dashboard displays
4. Test settings save functionality

## Adding New Admins

To add a new admin user:

1. **Update hardcoded list** in `backend-main.py` (line ~1201):
   ```python
   AUTHORIZED_ADMINS = {
       "test.reg.e2e+20251026@anwalts.ai",
       "angelageneralao.1997@gmail.com",
       "new.admin@example.com"  # Add new email
   }
   ```

2. **Update environment variable** in `docker-compose.yml`:
   ```yaml
   - ADMIN_EMAILS=test.reg.e2e+20251026@anwalts.ai,angelageneralao.1997@gmail.com,new.admin@example.com
   ```

3. **Update frontend composable** in `composables/useAuth.ts`:
   ```typescript
   const adminEmails = [
     'test.reg.e2e+20251026@anwalts.ai',
     'angelageneralao.1997@gmail.com',
     'new.admin@example.com'  // Add new email
   ]
   ```

4. **Set admin role in database**:
   ```sql
   UPDATE users SET role = 'admin' WHERE LOWER(email) = 'new.admin@example.com';
   ```

5. **Restart services**:
   ```bash
   docker restart anwalts_backend anwalts_frontend
   ```

## Security Notes

- Admin emails are hardcoded in source code for fail-safe access
- Environment variables provide additional flexibility
- Database role column serves as backup verification
- JWT token validation enforced on all admin API calls
- Session management uses httpOnly cookies
- All admin routes protected by middleware

## Troubleshooting

### "Access Denied" for valid admin
1. Check user email matches exactly (case-insensitive)
2. Verify database role: `SELECT role FROM users WHERE email = '...'`
3. Check backend logs for authentication errors
4. Verify JWT token is valid

### API returns 403 Forbidden
1. Verify Authorization header contains valid JWT
2. Check user role in database is 'admin'
3. Review backend middleware logs
4. Ensure AUTHORIZED_ADMINS list includes user email

### Statistics not displaying
1. Check database tables exist (users, email_accounts, documents, templates, api_tokens, webhooks)
2. Verify database connection in backend logs
3. Check for SQL errors in backend logs
4. Ensure user has is_active = true

### Settings not saving
1. Check organization_settings table exists
2. Verify user has admin role
3. Review backend logs for SQL errors
4. Ensure allowed_fields list includes the fields being updated

## Related Documentation
- OpenSpec proposal: `/root/openspec/changes/implement-admin-only-settings-dashboard/`
- Database schema: `/root/database.py`
- Backend endpoints: `/root/backend-main.py`
- Frontend composable: `/root/anwalts-frontend-new/composables/useAuth.ts`
- Settings page: `/root/anwalts-frontend-new/pages/dashboard/settings.vue`
