-- 0009_note_lifecycle.sql — the P3-06 substrate (RTM §2.5 item 7 + item 9
-- + §3.3's machine, SYS-01/02/03). THREE authoritative tables:
--   arv.note            the deep owner-authored Note — identity + immutable
--                       revisions + the AUTHORED long-form content; NO source
--                       binding by construction (the free-standing law: unlike
--                       the highlight/bookmark families there is no implicit
--                       source/anchor column set — the note's links are the
--                       EXPLICIT reference rows below; the diagram/structured-
--                       block contract is NOT frozen here, P4-C's reservation)
--   arv.note_lifecycle  §3.3's EVENT class (the 0007/0008 precedent): the
--                       tombstone/restore rows, append-only, the CURRENT view
--                       DERIVED from them (parity), never a state column
--   arv.note_reference  the explicit VERSION-AWARE references, PER-REVISION
--                       (each revision carries its own full set; a past
--                       revision's rows are immutable with it): kind IN
--                       work/source/anchor/highlight/note; a highlight/note
--                       reference MUST name the target revision (version-aware
--                       by construction — the reference pins the immutable
--                       (id, revision) pair, never a silent retarget); a
--                       work/source/anchor reference MUST NOT (the Source id
--                       IS the version; Work/Anchor carry no revision
--                       dimension) — note_reference_ref_shape_check; the
--                       TARGET must exist in the SAME owner scope (absent,
--                       another owner's, and a nonexistent target revision
--                       are the SAME refusal at the substrate — never a side
--                       channel); the set semantics enforced structurally
--                       (UNIQUE (note_id, note_revision, ref_kind, ref_id,
--                       owner_scope) — one reference per target per revision)
--
-- arv-baseline-bump: 1  (this file declares the note-family guards — procedural
-- constructs P3-M0's fail-closed grammar cannot classify; the 0007/0008
-- precedent: the directive is the owner-visible paper trail per PLAN's P3-M0
-- card.)
--
-- Conventions (the 0002/0004/0007/0008 substrate, unchanged):
--   id/created_at: NO defaults — adapters/ids + adapters/clock (LAW-24)
--   owner_scope/actor/provenance (run_id, input_hash): NOT NULL on every row (LAW-20/21)
--   append-only: the ARV-CAP-005 trigger (the 0004 guard, reused by name)
--   RLS: app.current_owner scopes arv_app; arv_read = BYPASSRLS auditor (LAW-22)
--   THE COMPOSITE-REFERENCE CONVENTION IN ITS TRIGGER FORM (0007/0008's
--     lesson): literal FKs onto revision-per-row entities cannot exist (the
--     entity pair is non-unique by construction); the guard triggers carry
--     the intent (existence in the SAME owner scope — absent and another
--     owner's the SAME refusal)
--   THE ALTERNATION INVARIANT (§3.3) AT THE SUBSTRATE: the advisory-xact-lock
--     serializes concurrent lifecycle/revision/reference writers on one note;
--     the named command-boundary refusals (ARV-NTE-002/004/005) remain the
--     clean first line, these guards are the race + hostile-direct-write
--     backstop
--   THE REVISION-APPEND GUARD (the #90 round-3 repair's convention, applied
--     from the start): every arv.note insert takes the SAME per-note advisory
--     xact lock; an append with revision > 1 on a tombstoned note is refused
--     with ARV-NTE-002 — the command boundary's locked build (commands.py's
--     build_txn phase) is never the only enforcement
--   NO command_log FK: idempotency_key is the command-log row's provenance ref
--     (the 0004/0007/0008 convention), not a second ledger

CREATE TABLE IF NOT EXISTS arv.note (
    id              UUID        NOT NULL,
    revision        INTEGER     NOT NULL CHECK (revision >= 1),
    content         TEXT        NOT NULL,
    owner_scope     TEXT        NOT NULL,
    actor           TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    run_id          TEXT        NOT NULL,
    input_hash      TEXT        NOT NULL,
    idempotency_key TEXT        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (id, revision)
);
CREATE INDEX IF NOT EXISTS note_owner ON arv.note (owner_scope, created_at);

CREATE TABLE IF NOT EXISTS arv.note_lifecycle (
    id              UUID        PRIMARY KEY,
    note_id         UUID        NOT NULL,
    event           TEXT        NOT NULL CHECK (event IN ('tombstone', 'restore')),
    owner_scope     TEXT        NOT NULL,
    actor           TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    run_id          TEXT        NOT NULL,
    input_hash      TEXT        NOT NULL,
    idempotency_key TEXT        NOT NULL,  -- the command-log row's provenance ref (never a second ledger)
    created_at      TIMESTAMPTZ NOT NULL,
    UNIQUE (id, owner_scope)
);
CREATE INDEX IF NOT EXISTS note_lifecycle_target ON arv.note_lifecycle (note_id, created_at, id);
CREATE INDEX IF NOT EXISTS note_lifecycle_owner  ON arv.note_lifecycle (owner_scope, created_at, id);

CREATE TABLE IF NOT EXISTS arv.note_reference (
    id              UUID        PRIMARY KEY,
    note_id         UUID        NOT NULL,
    note_revision   INTEGER     NOT NULL CHECK (note_revision >= 1),
    ref_kind        TEXT        NOT NULL CHECK (ref_kind IN ('work', 'source', 'anchor', 'highlight', 'note')),
    ref_id          UUID        NOT NULL,
    ref_revision    INTEGER,
    owner_scope     TEXT        NOT NULL,
    actor           TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    run_id          TEXT        NOT NULL,
    input_hash      TEXT        NOT NULL,
    idempotency_key TEXT        NOT NULL,  -- the command-log row's provenance ref (never a second ledger)
    created_at      TIMESTAMPTZ NOT NULL,
    UNIQUE (id, owner_scope),
    UNIQUE (note_id, note_revision, ref_kind, ref_id, owner_scope),
    CONSTRAINT note_reference_ref_shape_check CHECK (
        (ref_kind IN ('highlight', 'note') AND ref_revision IS NOT NULL AND ref_revision >= 1)
        OR (ref_kind IN ('work', 'source', 'anchor') AND ref_revision IS NULL)
    )
);
CREATE INDEX IF NOT EXISTS note_reference_note   ON arv.note_reference (note_id, note_revision, created_at, id);
CREATE INDEX IF NOT EXISTS note_reference_owner ON arv.note_reference (owner_scope, created_at, id);

-- the lifecycle insert guard: existence-in-scope + the §3.3 alternation parity
-- (the 0007/0008 form — every insert path serialized per-note and checked
-- against the committed rows)
CREATE OR REPLACE FUNCTION arv.enforce_note_lifecycle_guard() RETURNS trigger AS $$
DECLARE
    t_count INTEGER;
    r_count INTEGER;
BEGIN
    PERFORM pg_advisory_xact_lock(hashtext(NEW.note_id::text));
    IF NOT EXISTS (SELECT 1 FROM arv.note
                    WHERE id = NEW.note_id AND owner_scope = NEW.owner_scope) THEN
        RAISE EXCEPTION 'ARV-NTE-001: note % does not exist in the caller''s scope — absent and another owner''s are the SAME refusal at the substrate (the composite-reference guard)', NEW.note_id;
    END IF;
    SELECT count(*) FILTER (WHERE event = 'tombstone'),
           count(*) FILTER (WHERE event = 'restore')
      INTO t_count, r_count
      FROM arv.note_lifecycle
     WHERE note_id = NEW.note_id AND owner_scope = NEW.owner_scope;
    IF NEW.event = 'tombstone' AND t_count > r_count THEN
        RAISE EXCEPTION 'ARV-NTE-004: note % is already tombstoned — the §3.3 alternation is enforced at the substrate (tombstone only from active)', NEW.note_id;
    END IF;
    IF NEW.event = 'restore' AND t_count <= r_count THEN
        RAISE EXCEPTION 'ARV-NTE-005: note % is not tombstoned — the §3.3 alternation is enforced at the substrate (restore only from tombstoned)', NEW.note_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS note_lifecycle_guard ON arv.note_lifecycle;
CREATE TRIGGER note_lifecycle_guard BEFORE INSERT ON arv.note_lifecycle
    FOR EACH ROW EXECUTE FUNCTION arv.enforce_note_lifecycle_guard();

-- the revision-append guard (the #90 round-3 repair's convention, applied from
-- the start): the SAME advisory lock (a same-transaction re-acquisition is the
-- no-op PostgreSQL defines, so the command's own locked build never
-- self-blocks), the SAME parity derivation; a revision > 1 append on a
-- tombstoned note is the §3.3 violation refused with the named code at the
-- substrate. THE REVIEW ROUND'S STRENGTHENING (the independent verifier's V-1 +
-- the SEV's F2 — convergent, and claim-055 F7's routed hardening due at this
-- substrate-touching slice): the append must also name an EXISTING identity
-- (a revision > 1 for a never-created note is the phantom-identity gap —
-- ARV-NTE-001) and must be CONTIGUOUS (exactly max+1 — the §3.3 machine's
-- revision ladder; a hostile gap append is refused with ARV-NTE-011, the
-- ordinal backstop promoted from the PK alone to the named substrate refusal)
CREATE OR REPLACE FUNCTION arv.enforce_note_revision_guard() RETURNS trigger AS $$
DECLARE
    t_count INTEGER;
    r_count INTEGER;
    max_rev INTEGER;
BEGIN
    PERFORM pg_advisory_xact_lock(hashtext(NEW.id::text));
    IF NEW.revision = 1 THEN
        RETURN NEW;  -- the create path: a fresh identity carries no lifecycle state
    END IF;
    SELECT max(revision) INTO max_rev
      FROM arv.note
     WHERE id = NEW.id AND owner_scope = NEW.owner_scope;
    IF max_rev IS NULL THEN
        RAISE EXCEPTION 'ARV-NTE-001: note % does not exist in the caller''s scope — a revision append onto a never-created identity is the phantom-identity gap, refused at the substrate', NEW.id;
    END IF;
    SELECT count(*) FILTER (WHERE event = 'tombstone'),
           count(*) FILTER (WHERE event = 'restore')
      INTO t_count, r_count
      FROM arv.note_lifecycle
     WHERE note_id = NEW.id AND owner_scope = NEW.owner_scope;
    IF t_count > r_count THEN
        RAISE EXCEPTION 'ARV-NTE-002: note % is tombstoned — a revision append after tombstoning is refused at the substrate (§3.3: restore precedes edit)', NEW.id;
    END IF;
    IF NEW.revision <> max_rev + 1 THEN
        RAISE EXCEPTION 'ARV-NTE-011: the revision append for note % must be exactly max+1 (received % after max %) — the §3.3 revision ladder is contiguous, never a hostile gap (the ordinal backstop at the substrate)', NEW.id, NEW.revision, max_rev;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS note_revision_guard ON arv.note;
CREATE TRIGGER note_revision_guard BEFORE INSERT ON arv.note
    FOR EACH ROW EXECUTE FUNCTION arv.enforce_note_revision_guard();

-- the reference insert guard: the note (id, revision) the row belongs to must
-- exist in the SAME scope (ARV-NTE-007 — the hostile direct-write backstop;
-- a command's own same-transaction note row is visible here) AND the TARGET
-- must exist in the SAME scope per its kind (ARV-NTE-003 — absent, another
-- owner's, and a nonexistent target revision are the SAME refusal; the
-- version-aware shape itself is the CHECK constraint)
CREATE OR REPLACE FUNCTION arv.enforce_note_reference_guard() RETURNS trigger AS $$
DECLARE
    target_ok BOOLEAN;
BEGIN
    PERFORM pg_advisory_xact_lock(hashtext(NEW.note_id::text));
    IF NOT EXISTS (SELECT 1 FROM arv.note
                    WHERE id = NEW.note_id AND revision = NEW.note_revision
                      AND owner_scope = NEW.owner_scope) THEN
        RAISE EXCEPTION 'ARV-NTE-007: the note (%, %) this reference row belongs to does not exist in the caller''s scope — the per-revision reference binding is refused at the substrate', NEW.note_id, NEW.note_revision;
    END IF;
    IF NEW.ref_kind = 'work' THEN
        SELECT EXISTS (SELECT 1 FROM arv.work
                        WHERE id = NEW.ref_id AND owner_scope = NEW.owner_scope) INTO target_ok;
    ELSIF NEW.ref_kind = 'source' THEN
        SELECT EXISTS (SELECT 1 FROM arv.source
                        WHERE id = NEW.ref_id AND owner_scope = NEW.owner_scope) INTO target_ok;
    ELSIF NEW.ref_kind = 'anchor' THEN
        SELECT EXISTS (SELECT 1 FROM arv.anchor
                        WHERE id = NEW.ref_id AND owner_scope = NEW.owner_scope) INTO target_ok;
    ELSIF NEW.ref_kind = 'highlight' THEN
        SELECT EXISTS (SELECT 1 FROM arv.highlight
                        WHERE id = NEW.ref_id AND revision = NEW.ref_revision
                          AND owner_scope = NEW.owner_scope) INTO target_ok;
    ELSE
        SELECT EXISTS (SELECT 1 FROM arv.note
                        WHERE id = NEW.ref_id AND revision = NEW.ref_revision
                          AND owner_scope = NEW.owner_scope) INTO target_ok;
    END IF;
    IF NOT target_ok THEN
        RAISE EXCEPTION 'ARV-NTE-003: the referenced % (%, %) does not exist in the caller''s scope — absent, another owner''s, and a nonexistent target revision are the SAME refusal at the substrate (never a side channel)', NEW.ref_kind, NEW.ref_id, COALESCE(NEW.ref_revision::text, '-');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS note_reference_guard ON arv.note_reference;
CREATE TRIGGER note_reference_guard BEFORE INSERT ON arv.note_reference
    FOR EACH ROW EXECUTE FUNCTION arv.enforce_note_reference_guard();

-- the append-only guards (ARV-CAP-005, the 0004 function reused by name — one
-- guard function, every authoritative table)
DROP TRIGGER IF EXISTS note_immutable ON arv.note;
CREATE TRIGGER note_immutable BEFORE UPDATE OR DELETE ON arv.note
    FOR EACH ROW EXECUTE FUNCTION arv.reject_capture_mutation();
DROP TRIGGER IF EXISTS note_lifecycle_immutable ON arv.note_lifecycle;
CREATE TRIGGER note_lifecycle_immutable BEFORE UPDATE OR DELETE ON arv.note_lifecycle
    FOR EACH ROW EXECUTE FUNCTION arv.reject_capture_mutation();
DROP TRIGGER IF EXISTS note_reference_immutable ON arv.note_reference;
CREATE TRIGGER note_reference_immutable BEFORE UPDATE OR DELETE ON arv.note_reference
    FOR EACH ROW EXECUTE FUNCTION arv.reject_capture_mutation();

ALTER TABLE arv.note ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.note FORCE ROW LEVEL SECURITY;
ALTER TABLE arv.note_lifecycle ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.note_lifecycle FORCE ROW LEVEL SECURITY;
ALTER TABLE arv.note_reference ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.note_reference FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS owner_isolation ON arv.note;
CREATE POLICY owner_isolation ON arv.note FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));
DROP POLICY IF EXISTS owner_isolation ON arv.note_lifecycle;
CREATE POLICY owner_isolation ON arv.note_lifecycle FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));
DROP POLICY IF EXISTS owner_isolation ON arv.note_reference;
CREATE POLICY owner_isolation ON arv.note_reference FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

GRANT INSERT, SELECT ON arv.note TO arv_app;
GRANT SELECT ON arv.note TO arv_read;
GRANT INSERT, SELECT ON arv.note_lifecycle TO arv_app;
GRANT SELECT ON arv.note_lifecycle TO arv_read;
GRANT INSERT, SELECT ON arv.note_reference TO arv_app;
GRANT SELECT ON arv.note_reference TO arv_read;
