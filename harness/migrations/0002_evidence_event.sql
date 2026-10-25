-- 0002_evidence_event.sql — the substrate-convention table (S2; D-036; Rider A:

-- arv-baseline-bump: 1  (P3-M0's admitted grammar: this file declares the plpgsql immutability trigger
-- function — a procedural construct the fail-closed grammar cannot classify; the directive is the
-- owner-visible paper trail that admits it, per PLAN's P3-M0 card / ARV-MIG-015.)
-- the Phase 2 exit's "evidence immutability, owner scoping, independent reads"
-- proven on ONE representative table carrying every convention).
--
-- Conventions carried (each maps to a law whose product form lands in Phase 3):
--   owner_scope  NOT NULL             — every write carries an owner (LAW-21)
--   actor        NOT NULL + closed vocabulary — authorship is schema-level (LAW-21/§3.1)
--   run_id, input_hash NOT NULL       — provenance on every row (LAW-20's shape, evidence-grade)
--   created_at   NOT NULL, NO DEFAULT — the clock adapter supplies it (LAW-24)
--   id           UUID PK, NO DEFAULT  — the ids adapter supplies it (LAW-24)
--   revisions/tombstones             — NEW rows (event_type + ref_id), never mutations
--   immutability                      — BEFORE UPDATE/DELETE trigger, named code ARV-EV-001 (LAW-19)
--   owner isolation                   — RLS vs app.current_owner for arv_app; arv_read = BYPASSRLS auditor (LAW-22)
--
-- The owner-run purge (D-011) is the only authorized erasure — Phase 3+; until
-- then the trigger is absolute (even the migrator's UPDATE/DELETE is rejected).

CREATE TABLE IF NOT EXISTS arv.evidence_event (
    id          UUID        PRIMARY KEY,
    event_type  TEXT        NOT NULL CHECK (event_type IN ('event', 'revision', 'tombstone')),
    payload     TEXT        NOT NULL,
    owner_scope TEXT        NOT NULL,
    actor       TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    run_id      TEXT        NOT NULL,
    input_hash  TEXT        NOT NULL,
    ref_id      UUID        NULL,
    created_at  TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS evidence_event_owner ON arv.evidence_event (owner_scope, created_at);
CREATE INDEX IF NOT EXISTS evidence_event_ref   ON arv.evidence_event (ref_id) WHERE ref_id IS NOT NULL;

-- Immutability (LAW-19 analog): the named code IS the diagnostics contract.
CREATE OR REPLACE FUNCTION arv.reject_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'ARV-EV-001: evidence rows are immutable (LAW-19 analog) — % on arv.evidence_event id=% rejected; revisions and tombstones are NEW rows; the owner-run purge is the only authorized erasure (D-011)', TG_OP, OLD.id;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS evidence_event_immutable ON arv.evidence_event;
CREATE TRIGGER evidence_event_immutable
    BEFORE UPDATE OR DELETE ON arv.evidence_event
    FOR EACH ROW EXECUTE FUNCTION arv.reject_mutation();

-- Owner isolation (LAW-22 analog): arv_app sees/writes only its session owner's
-- rows. current_setting(..., true) is NULL when unset -> the policy fails CLOSED
-- (an unscoped session reads nothing and can write nothing).
ALTER TABLE arv.evidence_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.evidence_event FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS owner_isolation ON arv.evidence_event;
CREATE POLICY owner_isolation ON arv.evidence_event
    FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

-- The application path writes; the auditor reads (independent, sees all owners).
GRANT INSERT, SELECT ON arv.evidence_event TO arv_app;
GRANT SELECT ON arv.evidence_event TO arv_read;
