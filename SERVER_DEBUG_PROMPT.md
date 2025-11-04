# Email Display Issue - Server Diagnostic Prompt

## PROBLEM SUMMARY
User completes Google OAuth successfully, Gmail account is linked to database with all correct permissions, but the email page (`/email`) shows the consent screen instead of emails. Frontend console shows: "Gmail not connected, showing consent screen"

## CONFIRMED WORKING
1. ✅ OAuth flow completes successfully (logs show "Gmail account angelageneralao.1997@gmail.com linked")
2. ✅ Database has correct data:
   - `email_accounts` table: `oauth_consent=true`, `ai_read_consent=true`, `revoked_at=NULL`
   - `user_email_preferences` table: Correctly links `user_id` to `active_account_id`
3. ✅ Backend returns 200 OK for `/api/user/gmail/status`

## THE BUG
The `/api/user/gmail/status` endpoint returns `connected: false` even though database shows the account is properly linked.

## DATABASE STATE (Verified Correct)
```sql
-- email_accounts table
SELECT email_address, oauth_consent, ai_read_consent, revoked_at 
FROM email_accounts;
-- Result: angelageneralao.1997@gmail.com | t | t | NULL

-- user_email_preferences table  
SELECT user_id, active_account_id FROM user_email_preferences;
-- Result: 32c0e4e0-2c5d-4ad0-9729-57dbdf41c83e | 5b275e72-fad4-4da5-a449-5127ca190dec

-- JOIN verification (should return 1 row)
SELECT COUNT(*) FROM user_email_preferences pref 
JOIN email_accounts ea ON pref.active_account_id = ea.id 
WHERE pref.user_id = '32c0e4e0-2c5d-4ad0-9729-57dbdf41c83e' 
AND ea.revoked_at IS NULL;
-- Result: 1
```

## KEY FILES
- **Backend API**: `/app/backend-main.py` inside Docker container `anwalts_backend`
- **Database functions**: `/app/database.py` inside Docker container `anwalts_backend`
- **Frontend page**: `/root/anwalts-frontend-new/pages/email.vue`

## SUSPECTED ISSUES

### Theory 1: Database Function Returns None
The `get_active_email_account()` function in `database.py` might be:
- Hitting an exception in the try/catch block
- The `_serialize_email_account()` method might be failing
- The migration function `_maybe_migrate_profile_email_account()` might be interfering

### Theory 2: User ID Mismatch
The `current_user.id` passed to the endpoint might not match the database user_id

### Theory 3: Cached Response
Frontend or API gateway might be caching the old `connected: false` response

## YOUR TASK

You have direct SSH access to `root@148.251.195.222`. Please:

### Step 1: Add Real-Time Debugging
Add logging to `/app/backend-main.py` inside the `anwalts_backend` container at line 1958:

```python
status = await db.get_gmail_connection_status(current_user.id)
# ADD THIS:
import sys
print(f"[DEBUG STATUS] user_id={current_user.id}, status={status}", file=sys.stderr, flush=True)
```

Then restart the container and capture the output when the user refreshes the page.

### Step 2: Test the Database Query Directly
From inside the `anwalts_backend` container, run:

```python
python3 -c "
import asyncio
import asyncpg
from database import Database

async def test():
    db = Database('postgresql://anwalts_user:anwalts_password@postgres:5432/anwalts_ai')
    await db._create_pool()
    result = await db.get_active_email_account('32c0e4e0-2c5d-4ad0-9729-57dbdf41c83e')
    print('Active account:', result)
    status = await db.get_gmail_connection_status('32c0e4e0-2c5d-4ad0-9729-57dbdf41c83e')
    print('Status:', status)

asyncio.run(test())
"
```

### Step 3: Check Network Tab Response
Have the user open DevTools → Network tab → Refresh → Click on `status` request → Response tab.
Copy the exact JSON response from `/api/user/gmail/status`.

### Step 4: Fix the Root Cause
Once you identify why `connected: false` is being returned:

**If database query returns None:**
- Check if `_serialize_email_account()` is failing
- Check if `_maybe_migrate_profile_email_account()` is clearing data
- Add error logging to `get_active_email_account()`

**If user ID mismatch:**
- Log the actual `current_user.id` being used
- Verify JWT token is correct
- Check session validation

**If caching:**
- Clear browser cache
- Add no-cache headers to the status endpoint
- Check if NGINX is caching the response

### Step 5: Verify the Fix
After fixing, the API should return:
```json
{
  "connected": true,
  "ai_read_consent": true,
  "oauth_consent": true,
  "active_account": { ... }
}
```

And the frontend should display the inbox with emails.

## IMPORTANT NOTES
- The Docker container `anwalts_backend` is running code from `/app/backend-main.py` (NOT `/root/backend-main.py`)
- Changes to `/root/backend-main.py` do NOT affect the running container
- To apply changes: Either rebuild the image OR copy files into the container with `docker exec`
- The frontend (`email.vue`) checks `data.connected` - if false, shows consent screen
- Database is PostgreSQL in container `anwalts_postgres`

## SUCCESS CRITERIA
User visits `https://portal-anwalts.ai/email` and sees their Gmail inbox with emails loaded, NOT the consent screen.

