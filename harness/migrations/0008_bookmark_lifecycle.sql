-- 0008_bookmark_lifecycle.sql — the P3-05 substrate (RTM §2.5 item 6
-- + §3.3's machine, SYS-01/02/05). TWO authoritative tables:
--   arv.bookmark          the stable return location — identity + the
--                         source-versioned Anchor/location reference,
--                         REVISION-PER-ROW (the 0004 highlight shape); NO
--                         content column exists by construction (the card's
--                         "do not duplicate source text" made structural —
--                         the location evidence lives in arv.anchor alone)
--   arv.bookmark_lifecycle §2.9's EVENT class (the 0007 precedent): the
--                         tombstone/restore rows, append-only, the CURRENT
--                         view DERIVED from them (parity), never a state
--                         column
--
-- arv-baseline-bump: 1  (this file declares the lifecycle guard — a procedural
-- construct P3-M0's fail-closed grammar cannot classify; the 0007 precedent:
-- the directive is the owner-visible paper trail per PLAN's P3-M0 card.)
--
-- Conventions (the 0002/0004/0007 substrate, unchanged):
--   id/created_at: NO defaults — adapters/ids + adapters/clock (LAW-24)
--   owner_scope/actor/provenance (run_id, input_hash): NOT NULL on every row (LAW-20/21)
--   append-only: the ARV-CAP-005 trigger (the 0004 guard, reused by name)
--   RLS: app.current_owner scopes arv_app; arv_read = BYPASSRLS auditor (LAW-22)
--   THE COMPOSITE-REFERENCE CONVENTION IN ITS TRIGGER FORM (0007's lesson): a
--     literal FK (bookmark_id, owner_scope) -> arv.bookmark cannot exist on
--     the revision-per-row shape (the entity pair is non-unique by
--     construction); the guard trigger carries the intent (existence in the
--     SAME owner scope — absent and another owner's the SAME refusal)
--   THE ALTERNATION INVARIANT (§3.3) AT THE SUBSTRATE: the advisory-xact-lock
--     serializes concurrent lifecycle writers on one bookmark; the named
--     command-boundary refusals (ARV-BMK-002/003/004) remain the clean first
--     line, this guard is the race + hostile-direct-write backstop
--   NO command_log FK: idempotency_key is the command-log row's provenance ref
--     (the 0004/0007 convention), not a second ledger

CREATE TABLE IF NOT EXISTS arv.bookmark (
    id              UUID        NOT NULL,
    revision        INTEGER     NOT NULL CHECK (revision >= 1),
    source_id       UUID        NOT NULL,
    anchor_id       UUID        NOT NULL,
    owner_scope     TEXT        NOT NULL,
    actor           TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    run_id          TEXT        NOT NULL,
    input_hash      TEXT        NOT NULL,
    idempotency_key TEXT        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (id, revision),
    FOREIGN KEY (source_id, owner_scope) REFERENCES arv.source (id, owner_scope),
    FOREIGN KEY (anchor_id, source_id, owner_scope) REFERENCES arv.anchor (id, source_id, owner_scope)
);
CREATE INDEX IF NOT EXISTS bookmark_owner ON arv.bookmark (owner_scope, created_at);

CREATE TABLE IF NOT EXISTS arv.bookmark_lifecycle (
    id              UUID        PRIMARY KEY,
    bookmark_id     UUID        NOT NULL,
    event           TEXT        NOT NULL CHECK (event IN ('tombstone', 'restore')),
    owner_scope     TEXT        NOT NULL,
    actor           TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    run_id          TEXT        NOT NULL,
    input_hash      TEXT        NOT NULL,
    idempotency_key TEXT        NOT NULL,  -- the command-log row's provenance ref (never a second ledger)
    created_at      TIMESTAMPTZ NOT NULL,
    UNIQUE (id, owner_scope)
);
CREATE INDEX IF NOT EXISTS bookmark_lifecycle_target ON arv.bookmark_lifecycle (bookmark_id, created_at, id);
CREATE INDEX IF NOT EXISTS bookmark_lifecycle_owner  ON arv.bookmark_lifecycle (owner_scope, created_at, id);

-- the ONE insert guard: existence-in-scope (the composite-FK intent in its
-- trigger form) + the §3.3 alternation parity — every insert path serialized
-- per-bookmark and checked against the committed rows
CREATE OR REPLACE FUNCTION arv.enforce_bookmark_lifecycle_guard() RETURNS trigger AS $$
DECLARE
    t_count INTEGER;
    r_count INTEGER;
BEGIN
    PERFORM pg_advisory_xact_lock(hashtext(NEW.bookmark_id::text));
    IF NOT EXISTS (SELECT 1 FROM arv.bookmark
                    WHERE id = NEW.bookmark_id AND owner_scope = NEW.owner_scope) THEN
        RAISE EXCEPTION 'ARV-BMK-001: bookmark % does not exist in the caller''s scope — absent and another owner''s are the SAME refusal at the substrate (the composite-reference guard)', NEW.bookmark_id;
    END IF;
    SELECT count(*) FILTER (WHERE event = 'tombstone'),
           count(*) FILTER (WHERE event = 'restore')
      INTO t_count, r_count
      FROM arv.bookmark_lifecycle
     WHERE bookmark_id = NEW.bookmark_id AND owner_scope = NEW.owner_scope;
    IF NEW.event = 'tombstone' AND t_count > r_count THEN
        RAISE EXCEPTION 'ARV-BMK-003: bookmark % is already tombstoned — the §3.3 alternation is enforced at the substrate (tombstone only from active)', NEW.bookmark_id;
    END IF;
    IF NEW.event = 'restore' AND t_count <= r_count THEN
        RAISE EXCEPTION 'ARV-BMK-004: bookmark % is not tombstoned — the §3.3 alternation is enforced at the substrate (restore only from tombstoned)', NEW.bookmark_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS bookmark_lifecycle_guard ON arv.bookmark_lifecycle;
CREATE TRIGGER bookmark_lifecycle_guard BEFORE INSERT ON arv.bookmark_lifecycle
    FOR EACH ROW EXECUTE FUNCTION arv.enforce_bookmark_lifecycle_guard();

-- the append-only guards (ARV-CAP-005, the 0004 function reused by name — one
-- guard function, every authoritative table)
DROP TRIGGER IF EXISTS bookmark_immutable ON arv.bookmark;
CREATE TRIGGER bookmark_immutable BEFORE UPDATE OR DELETE ON arv.bookmark
    FOR EACH ROW EXECUTE FUNCTION arv.reject_capture_mutation();
DROP TRIGGER IF EXISTS bookmark_lifecycle_immutable ON arv.bookmark_lifecycle;
CREATE TRIGGER bookmark_lifecycle_immutable BEFORE UPDATE OR DELETE ON arv.bookmark_lifecycle
    FOR EACH ROW EXECUTE FUNCTION arv.reject_capture_mutation();

ALTER TABLE arv.bookmark ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.bookmark FORCE ROW LEVEL SECURITY;
ALTER TABLE arv.bookmark_lifecycle ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.bookmark_lifecycle FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS owner_isolation ON arv.bookmark;
CREATE POLICY owner_isolation ON arv.bookmark FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));
DROP POLICY IF EXISTS owner_isolation ON arv.bookmark_lifecycle;
CREATE POLICY owner_isolation ON arv.bookmark_lifecycle FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

GRANT INSERT, SELECT ON arv.bookmark TO arv_app;
GRANT SELECT ON arv.bookmark TO arv_read;
GRANT INSERT, SELECT ON arv.bookmark_lifecycle TO arv_app;
GRANT SELECT ON arv.bookmark_lifecycle TO arv_read;
