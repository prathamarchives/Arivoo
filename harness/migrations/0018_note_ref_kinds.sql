-- 0018_note_ref_kinds.sql — P4-D SLICE TWO (CLAIM-076; record 68 §2): the
-- note-reference write completion — the seven-family @-reference system's
-- write boundary. The bounded increment CLAIM-075's own not-verified list
-- named: bookmark/journal_block references were RESOLVABLE through the
-- resolution surface but not yet WRITABLE through note --ref (the 0010
-- vocabulary predates the journal family's landing and never included the
-- bookmark). A reference system where two of the seven families can never
-- be STORED is incomplete; this widening completes it.
--
-- THE WIDENING IS EXACTLY TWO KINDS, never an open enum: ref_kind gains
-- 'bookmark' and 'journal_block'; both join the REVISIONED arm of the shape
-- law (ref_revision IS NOT NULL AND >= 1 — both families are revision
-- tables; a stored reference pins the immutable (id, revision) pair,
-- version-aware by construction, the substrate's own law). work/source/
-- anchor stay bare (the identity IS the version); highlight/note stay
-- revisioned. The guard's per-kind target checks gain the two arms — the
-- bookmark arm reads arv.bookmark at the pinned revision, the journal arm
-- reads arv.journal_block at the pinned revision (both owner-scoped — the
-- same ARV-NTE-003 no-oracle as every other arm; the ELSE arm stays the
-- NOTE family's own, never a catch-all).
--
-- arv-baseline-bump: 1  (the constraint drops are the destructive class —
-- ARV-MIG-003's owner-visible paper trail; the drops and re-adds ride the
-- runner's ONE transaction with this file's bookkeeping row, and the
-- replacement guard function is the procedural construct the admitted
-- grammar cannot classify — the 0010 convention)
ALTER TABLE arv.note_reference DROP CONSTRAINT note_reference_ref_kind_check;
ALTER TABLE arv.note_reference ADD CONSTRAINT note_reference_ref_kind_check
    CHECK (ref_kind IN ('work', 'source', 'anchor', 'highlight', 'note',
                        'bookmark', 'journal_block'));
ALTER TABLE arv.note_reference DROP CONSTRAINT note_reference_ref_shape_check;
ALTER TABLE arv.note_reference ADD CONSTRAINT note_reference_ref_shape_check CHECK (
    (ref_kind IN ('highlight', 'note', 'bookmark', 'journal_block')
         AND ref_revision IS NOT NULL AND ref_revision >= 1)
    OR (ref_kind IN ('work', 'source', 'anchor') AND ref_revision IS NULL)
);

-- the widened insert guard: the per-revision note binding unchanged
-- (ARV-NTE-007); the target existence-in-scope per kind gains the two
-- arms — bookmark reads arv.bookmark at the pinned revision, journal_block
-- reads arv.journal_block at the pinned revision (both owner-scoped; the
-- same ARV-NTE-003 refusal as the command boundary, never a side channel).
-- The advisory xact lock is the note's OWN canonical key (unchanged).
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
    ELSIF NEW.ref_kind = 'bookmark' THEN
        SELECT EXISTS (SELECT 1 FROM arv.bookmark
                        WHERE id = NEW.ref_id AND revision = NEW.ref_revision
                          AND owner_scope = NEW.owner_scope) INTO target_ok;
    ELSIF NEW.ref_kind = 'journal_block' THEN
        SELECT EXISTS (SELECT 1 FROM arv.journal_block
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
