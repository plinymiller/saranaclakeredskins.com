-- D1 schema for the alumni sign-up Worker
CREATE TABLE IF NOT EXISTS signups (
  id            TEXT PRIMARY KEY,            -- random id
  first_name    TEXT NOT NULL,
  last_name     TEXT NOT NULL,
  school_last   TEXT,                        -- last name in high school, if different
  class_year    INTEGER NOT NULL,
  email         TEXT NOT NULL,
  status        TEXT NOT NULL,               -- pending_email | review | verified | approved | rejected | banned
  match_type    TEXT NOT NULL,               -- exact | other_year | none
  match_detail  TEXT,                        -- JSON: matched names/years from alumni.json
  token_hash    TEXT,                        -- SHA-256 of the email verification token
  token_expires INTEGER,                     -- unix seconds
  ip_hash       TEXT,                        -- SHA-256(ip + salt), never the raw IP
  created_at    INTEGER NOT NULL,
  verified_at   INTEGER,
  reviewed_at   INTEGER,
  reviewer_note TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS signups_email ON signups(email);
CREATE INDEX IF NOT EXISTS signups_status ON signups(status);
