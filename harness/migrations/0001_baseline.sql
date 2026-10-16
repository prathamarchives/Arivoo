-- 0001_baseline.sql — the Phase 2 Layer 2.1 baseline (S1, D-036; 2026-10-16).
-- The migrations bookkeeping table + the rig's role model (S2 grants the substrate
-- table to these roles). Destructive statements in any LATER migration require an
-- explicit "-- arv-baseline-bump:" directive or the runner refuses (ARV-MIG-003).
-- applied_at uses the DB clock by design: this is RUNNER metadata, not substrate
-- data — substrate rows take created_at as a PARAMETER from adapters/clock (S2, LAW-24).

CREATE SCHEMA IF NOT EXISTS arv;

CREATE TABLE IF NOT EXISTS arv.schema_migrations (
    version     BIGINT PRIMARY KEY,
    name        TEXT NOT NULL,
    checksum    TEXT NOT NULL,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    applied_by  TEXT NOT NULL
);

-- The rig's role model:
--   arv_app  — the application path (writes; S2 grants the substrate table)
--   arv_read — the independent verification oracle (read-only, BYPASSRLS so it can
--              observe every owner's rows — LAW-13/LAW-22: the two-owner test is
--              enforced on the APP role; the auditor's job is to see the truth)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'arv_app') THEN
        CREATE ROLE arv_app LOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'arv_read') THEN
        CREATE ROLE arv_read LOGIN BYPASSRLS;
    END IF;
END
$$;

GRANT USAGE ON SCHEMA arv TO arv_app, arv_read;
GRANT SELECT ON arv.schema_migrations TO arv_app, arv_read;
