-- 0010_note_references.sql — P3-06 SLICE TWO (CLAIM-057; RTM §2.5 item 7):
-- the explicit VERSION-AWARE references, PER-REVISION rows. The LAW-05 split
-- (the 9608a3a record) re-homed this machine from the pre-split 0009 draft
-- to its own migration — the note CORE (arv.note + arv.note_lifecycle + its
-- guards) landed as 0009 with PR #91; this slice adds the reference substrate
-- the --ref surface rides. Shape law: highlight/note refs MUST name the
-- target revision (the immutable (id, revision) pair is what a reference
-- MEANS — never a silent retarget); work/source/anchor MUST NOT (the Source
-- id IS the version; Work/Anchor carry no revision dimension) — the
-- note_reference_ref_shape_check. Set semantics: one reference per target per
-- revision. The target-existence + caller-scope guard fires at the substrate
-- (ARV-NTE-003 — absent, another owner's, and a nonexistent target revision
-- are the SAME refusal, never a side channel) beside the command boundary's
-- own check (the 0007/0008 convention: both layers, never one alone).
-- arv-baseline-bump: 1  (this file declares the reference guard — a procedural
-- construct the admitted grammar cannot classify; the owner-visible paper
-- trail per ARV-MIG-015, the 0007/0008/0009 convention)
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

-- the reference insert guard: the per-revision note binding must exist in the
-- caller's scope (ARV-NTE-007 — a reference row cannot outrun its own note
-- revision), then the target existence-in-scope per kind (ARV-NTE-003 — the
-- same refusal as the command boundary, never a side channel). The advisory
-- xact lock is the note's OWN canonical key (the 0009 guards' key): a hostile
-- insert serializes with the note family's own transitions.
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

-- the append-only guard (ARV-CAP-005, the 0004 function reused by name — one
-- guard function, every authoritative table)
DROP TRIGGER IF EXISTS note_reference_immutable ON arv.note_reference;
CREATE TRIGGER note_reference_immutable BEFORE UPDATE OR DELETE ON arv.note_reference
    FOR EACH ROW EXECUTE FUNCTION arv.reject_capture_mutation();

ALTER TABLE arv.note_reference ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.note_reference FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS owner_isolation ON arv.note_reference;
CREATE POLICY owner_isolation ON arv.note_reference FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

GRANT INSERT, SELECT ON arv.note_reference TO arv_app;
GRANT SELECT ON arv.note_reference TO arv_read;
