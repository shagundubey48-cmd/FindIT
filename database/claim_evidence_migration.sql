-- Only for databases created BEFORE this column existed.
-- Fresh installs already include it (see schema.sql / claims.sql).
USE finditplus;

ALTER TABLE claims
ADD COLUMN proof_type VARCHAR(50) NULL,
ADD COLUMN proof_details TEXT NULL;
