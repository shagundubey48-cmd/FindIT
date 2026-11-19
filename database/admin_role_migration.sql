-- Only for databases created BEFORE this column existed.
-- Fresh installs already include it (see schema.sql / claims.sql).
USE finditplus;

ALTER TABLE users
ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE;
