-- AIVersus Database Schema Initialization
-- This script runs automatically when the PostgreSQL container starts for the first time.

CREATE TABLE IF NOT EXISTS "user" (
    name     VARCHAR(255),
    email    VARCHAR(255) NOT NULL PRIMARY KEY,
    password VARCHAR(255),
    disabled BOOLEAN NOT NULL DEFAULT FALSE
);

-- For an already-existing database (created before the `disabled` column),
-- run this once to add it (safe to re-run):
--   ALTER TABLE "user" ADD COLUMN IF NOT EXISTS disabled BOOLEAN NOT NULL DEFAULT FALSE;

CREATE TABLE IF NOT EXISTS chat_history (
    id           VARCHAR(255) NOT NULL PRIMARY KEY,
    user_email   VARCHAR(255),
    queries      TEXT[],
    response     TEXT[],
    response2    TEXT[],
    response3    TEXT[],
    last_updated TIMESTAMP
);
