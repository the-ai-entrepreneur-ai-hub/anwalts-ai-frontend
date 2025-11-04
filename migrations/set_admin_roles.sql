-- Migration: Set admin roles for authorized emails
-- Created: 2025-11-02
-- Purpose: Promote authorized users to admin role for admin-only settings dashboard

-- Set admin roles for authorized emails
UPDATE users 
SET role = 'admin' 
WHERE LOWER(email) IN (
  'test.reg.e2e+20251026@anwalts.ai',
  'angelageneralao.1997@gmail.com'
);

-- Verify the update
SELECT id, email, role, created_at 
FROM users 
WHERE role = 'admin'
ORDER BY email;
