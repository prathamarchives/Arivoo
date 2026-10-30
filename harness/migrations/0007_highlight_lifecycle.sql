-- 0007_highlight_lifecycle.sql — the P3-04 lifecycle substrate (RTM §2.5 item 5
-- + §3.3's machine, SYS-02/05). §2.9's authoritative EVENT class: the lifecycle
-- rows are governed history — append-only, owner-scoped, provenance-complete;
-- the CURRENT view (active | tombstoned) is DERIVED from them (parity: the
-- tombstone count vs the restore count — order-independent, rebuildable), never
-- a state column duplicating a derivable fact.
--
-- arv-baseline-bump: 1  (this file declares the lifecycle guard — a procedural
-- construct P3-M0's fail-closed grammar cannot classify; the directive is the
-- owner-visible paper trail per PLAN's P3-M0 card, the 0004_baseline precedent:
-- ARV-CAP-005's function is the same class.)

-- Conventions (the 0002/0004 substrate, extended to the event class):
--   id/created_at: NO defaults — adapters/ids + adapters/clock (LAW-24)
--   owner_scope/actor/provenance (run_id, input_hash): NOT NULL on every row (LAW-20/21)
--   append-only: the ARV-CAP-005 trigger (the 0004 guard, reused by name)
--   RLS: app.current_owner scopes arv_app; arv_read = BYPASSRLS auditor (LAW-22)
--   THE COMPOSITE-REFERENCE CONVENTION IN ITS TRIGGER FORM: a literal
--     FOREIGN KEY (highlight_id, owner_scope) -> arv.highlight needs a unique
--     (id, owner_scope) target, but arv.highlight is REVISION-PER-ROW (PK
--     (id, revision) — 0004's shape; every revision row shares the identity),
--     so the entity-level pair is not unique and cannot back an FK.  The guard
--     trigger below enforces the SAME intent (the referenced highlight exists
--     in the SAME owner scope — absent and another owner's are the SAME
--     refusal, never a side channel) at the substrate, RLS-scoped like the
--     command boundary; the command layer's ARV-HLC-001 is the clean first line.
--   THE ALTERNATION INVARIANT (§3.3: tombstone only from active; restore only
--     from tombstoned) enforced AT THE SUBSTRATE: the advisory-xact-lock
--     serializes concurrent lifecycle writers on one highlight, so the
--     check-then-insert race cannot produce a non-alternating sequence; the
--     command boundary's named refusals (ARV-HLC-002/003/004) remain the clean
--     first line, this guard is the race + hostile-direct-write backstop
--   NO command_log FK: idempotency_key is the command-log row's provenance ref
--     (the 0004 highlight convention), not a second ledger

CREATE TABLE IF NOT EXISTS arv.highlight_lifecycle (
    id             UUID        PRIMARY KEY,
    highlight_id   UUID        NOT NULL,
    event          TEXT        NOT NULL CHECK (event IN ('tombstone', 'restore')),
    owner_scope    TEXT        NOT NULL,
    actor          TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    run_id         TEXT        NOT NULL,
    input_hash     TEXT        NOT NULL,
    idempotency_key TEXT       NOT NULL,  -- the command-log row's provenance ref (never a second ledger)
    created_at     TIMESTAMPTZ NOT NULL,
    UNIQUE (id, owner_scope)
);
CREATE INDEX IF NOT EXISTS highlight_lifecycle_target ON arv.highlight_lifecycle (highlight_id, created_at, id);
CREATE INDEX IF NOT EXISTS highlight_lifecycle_owner  ON arv.highlight_lifecycle (owner_scope, created_at, id);

-- the ONE insert guard: existence-in-scope (the composite-FK intent in its
-- trigger form) + the §3.3 alternation parity — every insert path (command,
-- hostile direct write, concurrent writer) is serialized per-highlight and
-- checked against the committed rows
CREATE OR REPLACE FUNCTION arv.enforce_lifecycle_guard() RETURNS trigger AS $$
DECLARE
    t_count INTEGER;
    r_count INTEGER;
BEGIN
    PERFORM pg_advisory_xact_lock(hashtext(NEW.highlight_id::text));
    IF NOT EXISTS (SELECT 1 FROM arv.highlight
                    WHERE id = NEW.highlight_id AND owner_scope = NEW.owner_scope) THEN
        RAISE EXCEPTION 'ARV-HLC-001: highlight % does not exist in the caller''s scope — absent and another owner''s are the SAME refusal at the substrate (the composite-reference guard)', NEW.highlight_id;
    END IF;
    SELECT count(*) FILTER (WHERE event = 'tombstone'),
           count(*) FILTER (WHERE event = 'restore')
      INTO t_count, r_count
      FROM arv.highlight_lifecycle
     WHERE highlight_id = NEW.highlight_id AND owner_scope = NEW.owner_scope;
    IF NEW.event = 'tombstone' AND t_count > r_count THEN
        RAISE EXCEPTION 'ARV-HLC-003: highlight % is already tombstoned — the §3.3 alternation is enforced at the substrate (tombstone only from active)', NEW.highlight_id;
    END IF;
    IF NEW.event = 'restore' AND t_count <= r_count THEN
        RAISE EXCEPTION 'ARV-HLC-004: highlight % is not tombstoned — the §3.3 alternation is enforced at the substrate (restore only from tombstoned)', NEW.highlight_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS lifecycle_guard ON arv.highlight_lifecycle;
CREATE TRIGGER lifecycle_guard BEFORE INSERT ON arv.highlight_lifecycle
    FOR EACH ROW EXECUTE FUNCTION arv.enforce_lifecycle_guard();

-- the append-only guard (ARV-CAP-005, the 0004 function reused by name — one
-- guard function, every authoritative table)
DROP TRIGGER IF EXISTS highlight_lifecycle_immutable ON arv.highlight_lifecycle;
CREATE TRIGGER highlight_lifecycle_immutable BEFORE UPDATE OR DELETE ON arv.highlight_lifecycle
    FOR EACH ROW EXECUTE FUNCTION arv.reject_capture_mutation();

ALTER TABLE arv.highlight_lifecycle ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.highlight_lifecycle FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS owner_isolation ON arv.highlight_lifecycle;
CREATE POLICY owner_isolation ON arv.highlight_lifecycle FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

GRANT INSERT, SELECT ON arv.highlight_lifecycle TO arv_app;
GRANT SELECT ON arv.highlight_lifecycle TO arv_read;
