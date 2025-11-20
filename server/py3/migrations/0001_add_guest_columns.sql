-- Add guest columns to sessions
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS guest_id TEXT;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS guest_name TEXT;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS guest_icon TEXT;
-- Create FK to users table if not exists (Postgres doesn't have IF NOT EXISTS for constraints, so check with DO block)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'fk_sessions_guest_id_users'
    ) THEN
        ALTER TABLE sessions ADD CONSTRAINT fk_sessions_guest_id_users FOREIGN KEY (guest_id) REFERENCES users(id);
    END IF;
END$$;
