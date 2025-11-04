# Tasks: stabilize-email-connection

- [x] 1. Instrument `/api/user/gmail/status` with the new serializer and status logging.
- [x] 2. Ensure `database.get_gmail_connection_status` and cache helpers cannot return asyncpg records; add unit tests.
- [x] 3. Namespace email connection state per Supabase user in `pages/email.vue` and remove consent flash.
- [x] 4. Add logout/login watcher to clear Gmail state and timers on user change.
- [x] 5. Write Playwright regression for user switch + rebuild scenarios.
- [x] 6. Run lint/tests, rebuild backend/frontend images, restart nginx, and capture smoke results.
