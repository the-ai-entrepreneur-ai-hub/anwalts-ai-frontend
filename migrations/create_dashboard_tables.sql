-- Dashboard Tables Migration
-- Created: 2025-11-02
-- Purpose: Add tables for dynamic dashboard data (cases, deadlines, activities)

-- ============================================================================
-- Table: cases
-- Stores user cases/matters
-- ============================================================================
CREATE TABLE IF NOT EXISTS cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    case_number VARCHAR(100),
    status VARCHAR(50) DEFAULT 'open',  -- open, pending, closed, archived
    client_name VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast user-specific queries
CREATE INDEX IF NOT EXISTS idx_cases_user_id ON cases(user_id);
-- Index for recent cases sorting
CREATE INDEX IF NOT EXISTS idx_cases_created_at ON cases(created_at DESC);
-- Index for filtering by status
CREATE INDEX IF NOT EXISTS idx_cases_status ON cases(status);

COMMENT ON TABLE cases IS 'Legal cases/matters assigned to users';
COMMENT ON COLUMN cases.user_id IS 'User (lawyer) responsible for this case';
COMMENT ON COLUMN cases.status IS 'Case status: open, pending, closed, archived';

-- ============================================================================
-- Table: deadlines
-- Stores task deadlines and appointments
-- ============================================================================
CREATE TABLE IF NOT EXISTS deadlines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    due_date TIMESTAMP NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',  -- low, medium, high, urgent
    related_case_id UUID REFERENCES cases(id) ON DELETE SET NULL,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast user-specific queries
CREATE INDEX IF NOT EXISTS idx_deadlines_user_id ON deadlines(user_id);
-- Composite index for upcoming deadlines query (user + not completed + due date)
CREATE INDEX IF NOT EXISTS idx_deadlines_upcoming ON deadlines(user_id, completed, due_date) WHERE completed = FALSE;
-- Index for due date sorting
CREATE INDEX IF NOT EXISTS idx_deadlines_due_date ON deadlines(due_date);
-- Index for completed status filtering
CREATE INDEX IF NOT EXISTS idx_deadlines_completed ON deadlines(completed);

COMMENT ON TABLE deadlines IS 'Task deadlines and appointments for users';
COMMENT ON COLUMN deadlines.priority IS 'Priority level: low, medium, high, urgent';
COMMENT ON COLUMN deadlines.related_case_id IS 'Optional reference to related case';

-- ============================================================================
-- Table: activities
-- Stores user activity log (emails, calls, uploads, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL,  -- email, phone, upload, meeting, note
    title VARCHAR(500) NOT NULL,
    description TEXT,
    related_entity_type VARCHAR(50),  -- case, document, deadline, etc.
    related_entity_id UUID,
    status VARCHAR(50),  -- pending, completed, review, etc.
    metadata JSONB,  -- Additional flexible data (email subject, file size, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast user-specific queries
CREATE INDEX IF NOT EXISTS idx_activities_user_id ON activities(user_id);
-- Composite index for recent activities query (user + created_at desc)
CREATE INDEX IF NOT EXISTS idx_activities_user_created ON activities(user_id, created_at DESC);
-- Index for activity type filtering
CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(activity_type);
-- Index for JSONB metadata queries
CREATE INDEX IF NOT EXISTS idx_activities_metadata ON activities USING GIN(metadata);

COMMENT ON TABLE activities IS 'User activity log for dashboard recent activity section';
COMMENT ON COLUMN activities.activity_type IS 'Type: email, phone, upload, meeting, note';
COMMENT ON COLUMN activities.metadata IS 'Flexible JSONB field for type-specific data';

-- ============================================================================
-- Modify existing documents table
-- Add columns for dashboard functionality if they don't exist
-- ============================================================================

-- Add user_id if missing (may already exist)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='documents' AND column_name='user_id') THEN
        ALTER TABLE documents ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Add progress column (0-100 percentage)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='documents' AND column_name='progress') THEN
        ALTER TABLE documents ADD COLUMN progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100);
    END IF;
END $$;

-- Add status column
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='documents' AND column_name='status') THEN
        ALTER TABLE documents ADD COLUMN status VARCHAR(50) DEFAULT 'draft';
    END IF;
END $$;

-- Add updated_at column if missing
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='documents' AND column_name='updated_at') THEN
        ALTER TABLE documents ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
END $$;

-- Create index on user_id for fast filtering
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
-- Composite index for recent documents query
CREATE INDEX IF NOT EXISTS idx_documents_user_updated ON documents(user_id, updated_at DESC) WHERE user_id IS NOT NULL;

COMMENT ON COLUMN documents.user_id IS 'User who owns/created this document';
COMMENT ON COLUMN documents.progress IS 'Document completion percentage (0-100)';
COMMENT ON COLUMN documents.status IS 'Document status: draft, in_progress, review, final';

-- ============================================================================
-- Trigger: Update updated_at timestamp automatically
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for cases table
DROP TRIGGER IF EXISTS update_cases_updated_at ON cases;
CREATE TRIGGER update_cases_updated_at
    BEFORE UPDATE ON cases
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for deadlines table
DROP TRIGGER IF EXISTS update_deadlines_updated_at ON deadlines;
CREATE TRIGGER update_deadlines_updated_at
    BEFORE UPDATE ON deadlines
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for activities table
DROP TRIGGER IF EXISTS update_activities_updated_at ON activities;
CREATE TRIGGER update_activities_updated_at
    BEFORE UPDATE ON activities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for documents table (only if column exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name='documents' AND column_name='updated_at') THEN
        DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
        CREATE TRIGGER update_documents_updated_at
            BEFORE UPDATE ON documents
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- ============================================================================
-- Sample data for testing (optional - comment out for production)
-- ============================================================================

-- Insert sample cases for testing (using admin user)
-- Uncomment these lines if you want test data:
/*
INSERT INTO cases (user_id, title, case_number, status, client_name, description) VALUES
((SELECT id FROM users WHERE email = 'angelageneralao.1997@gmail.com' LIMIT 1), 
 'Mietrechtsstreit M?ller', '2024-MR-001', 'open', 'Herr M?ller', 
 'R?umungsklage wegen Mietr?ckst?nden'),
((SELECT id FROM users WHERE email = 'angelageneralao.1997@gmail.com' LIMIT 1), 
 'Arbeitsrecht Schmidt GmbH', '2024-AR-015', 'open', 'Schmidt GmbH', 
 'K?ndigungsschutzklage');

INSERT INTO deadlines (user_id, title, description, due_date, priority) VALUES
((SELECT id FROM users WHERE email = 'angelageneralao.1997@gmail.com' LIMIT 1), 
 'Berufungsschrift einreichen', 'OLG M?nchen', CURRENT_TIMESTAMP + INTERVAL '3 days', 'urgent'),
((SELECT id FROM users WHERE email = 'angelageneralao.1997@gmail.com' LIMIT 1), 
 'Mandantentermin', 'Herr M?ller - Besprechung Vergleichsangebot', CURRENT_TIMESTAMP + INTERVAL '5 days', 'medium');

INSERT INTO activities (user_id, activity_type, title, description, status) VALUES
((SELECT id FROM users WHERE email = 'angelageneralao.1997@gmail.com' LIMIT 1), 
 'email', 'Anfrage von Mandant Schmidt', 'Frage zu K?ndigungsfrist', 'review'),
((SELECT id FROM users WHERE email = 'angelageneralao.1997@gmail.com' LIMIT 1), 
 'phone', 'R?ckruf Frau Meyer', 'Zeugenaussage besprechen', 'completed');
*/

-- ============================================================================
-- End of migration
-- ============================================================================
