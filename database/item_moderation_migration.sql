-- Only for databases created BEFORE this column existed.
-- Fresh installs already include it (see schema.sql / claims.sql).
USE finditplus;

ALTER TABLE items
ADD COLUMN admin_remarks TEXT NULL,
ADD COLUMN moderated_at DATETIME NULL;
