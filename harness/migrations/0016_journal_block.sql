-- 0016_journal_block.sql — P4-C slice three (CLAIM-072; PLAN's elaborated
-- P4-C slice three card; record 64 §2): the journal/blocks surface — the
-- writing lab (source-optional raw/creative blocks, long raw thinking
-- preserved losslessly, no forced short-note funnel).
--
-- THE BLOCK ROWS: append-only, owner-scoped, identity + immutable revisions
-- (the 0009 note-machine shape: PK (id, revision) and NOTHING unique over
-- (id, owner_scope) — a revision is a NEW row, the prior rows stay
-- untouched and accurate; replacement semantics. The 0015 single-row
-- families carry UNIQUE (id, owner_scope) because each event IS one row;
-- a revision table cannot — the second revision would violate it). The
-- content is TEXT — the LONG raw thinking preserved LOSSLESSLY (no length
-- cap, no truncation funnel; the write->read round-trip byte-honest).
--
-- THE CLOSED KIND VOCABULARY (the writing lab's own boundary, the 0015
-- D-010 pattern): kind IN ('raw', 'creative') — the raw thinking and the
-- creative writing, nothing else. The named CHECK below the command is the
-- second boundary: a hostile INSERT with an out-of-vocabulary kind (a
-- 'summary', a 'note', ...) refuses at the substrate.
--
-- THE SOURCE-OPTIONAL LAW: source_id NULL when the block is sourceless (a
-- FIRST-CLASS journal row — never a forced binding); the composite FK
-- (source_id, owner_scope) makes a bound block's reference owner-consistent
-- at the DB layer (the 0004 composite-FK law; MATCH SIMPLE leaves a NULL
-- binding unconstrained — the option IS structural).
--
-- THE NO-FORCED-FUNNEL LAW: no column exists to funnel the block into the
-- note machine's shape (no title, no summary, no max length); the journal
-- and the note are separate surfaces by construction (the no-conversion
-- law lives in the command path — a journal write never touches arv.note).
--
-- Conventions (the 0004/0009/0014/0015 substrate):
--   id/created_at: NO defaults — adapters/ids + adapters/clock (LAW-24)
--   owner_scope/actor/provenance (run_id, input_hash): NOT NULL (LAW-20/21)
--   RLS: app.current_owner scopes arv_app; arv_read = BYPASSRLS auditor (LAW-22)
--   append-only: UPDATE/DELETE refused (ARV-JNL-006, the 0004 pattern)
--   THE SERIALIZED REVISION (the 0009 pattern): every insert takes the SAME
--     per-block advisory xact lock the command takes — hashtext(id::text),
--     the bare canonical uuid rendering, NEVER a second key form
--   THE SOURCE-BIND LAW (ARV-JNL-008, checked FIRST): a bound block's
--     source must exist in the caller's scope (the composite FK's named
--     guard form — the honest code, never a bare FK violation)
--   THE REVISION-CONTIGUITY LAW (ARV-JNL-007, checked second): a revision
--     takes max(revision)+1 under the lock — no skips, no phantoms
--
-- arv-baseline-bump: 2  (this file declares the guard triggers — procedural
-- constructs the fail-closed grammar cannot classify; NO existing table is
-- altered: the family's <block>@<revision> address rides the TEXT
-- result_ref column 0014 widened)

CREATE TABLE IF NOT EXISTS arv.journal_block (
    id              UUID        NOT NULL,
    revision        INTEGER     NOT NULL CHECK (revision >= 1),
    kind            TEXT        NOT NULL,
    content         TEXT        NOT NULL,  -- THE LOSSLESS LAW: the long raw thinking, whole
    source_id       UUID,                  -- NULL when sourceless (the source-OPTIONAL law)
    owner_scope     TEXT        NOT NULL,
    actor           TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    run_id          TEXT        NOT NULL,
    input_hash      TEXT        NOT NULL,
    idempotency_key TEXT        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (id, revision),
    FOREIGN KEY (source_id, owner_scope) REFERENCES arv.source (id, owner_scope),
    CONSTRAINT journal_block_kind_check
        CHECK (kind IN ('raw', 'creative'))  -- the writing lab's closed vocabulary, structural
);
-- the (id, revision) PK serves the read arm's per-block history walk; the
-- listing orders by the block id (the keyset convention every list arm rides).

CREATE OR REPLACE FUNCTION arv.enforce_journal_block_guard() RETURNS trigger AS $$
DECLARE
    nxt INTEGER;
    src_n INTEGER;
BEGIN
    -- the serialized revision (the 0009 pattern): the SAME advisory lock the
    -- command takes — hashtext(id::text), the bare canonical uuid rendering —
    -- so hostile writers serialize behind the command path on ONE key
    PERFORM pg_advisory_xact_lock(hashtext(NEW.id::text));
    -- the source-bind law FIRST (ARV-JNL-008): a bound block's source must
    -- exist in the caller's scope — the composite FK's named guard form, the
    -- honest code before any bare FK violation; checked before the contiguity
    -- law so a hostile bind names ITS own defect, not the revision's
    IF NEW.source_id IS NOT NULL THEN
        SELECT count(*) INTO src_n FROM arv.source
            WHERE id = NEW.source_id AND owner_scope = NEW.owner_scope;
        IF src_n = 0 THEN
            RAISE EXCEPTION 'ARV-JNL-008: the bound block''s source % is not in the caller''s scope — the source-OPTIONAL binding never crosses owners (the no-oracle at the binding)', NEW.source_id;
        END IF;
    END IF;
    -- the revision-contiguity law SECOND (ARV-JNL-007): a revision takes
    -- max+1 under the lock (no skips, no phantoms)
    SELECT COALESCE(max(revision), 0) + 1 INTO nxt FROM arv.journal_block
        WHERE id = NEW.id AND owner_scope = NEW.owner_scope;
    IF NEW.revision <> nxt THEN
        RAISE EXCEPTION 'ARV-JNL-007: the journal block revision % is not the next lawful revision (%) for block % — revisions are contiguous, append-only rows (the governed history every landed family carries)', NEW.revision, nxt, NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION arv.reject_journal_block_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'ARV-JNL-006: % on %.% is refused — journal blocks are append-only (revisions are NEW rows; the governed purge is the only authorized erasure, D-011)', TG_OP, TG_TABLE_SCHEMA, TG_TABLE_NAME;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS journal_block_guard ON arv.journal_block;
CREATE TRIGGER journal_block_guard BEFORE INSERT ON arv.journal_block
    FOR EACH ROW EXECUTE FUNCTION arv.enforce_journal_block_guard();
DROP TRIGGER IF EXISTS journal_block_immutable ON arv.journal_block;
CREATE TRIGGER journal_block_immutable BEFORE UPDATE OR DELETE ON arv.journal_block
    FOR EACH ROW EXECUTE FUNCTION arv.reject_journal_block_mutation();

ALTER TABLE arv.journal_block ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.journal_block FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS owner_isolation ON arv.journal_block;
CREATE POLICY owner_isolation ON arv.journal_block FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

GRANT INSERT, SELECT ON arv.journal_block TO arv_app;
GRANT SELECT ON arv.journal_block TO arv_read;
