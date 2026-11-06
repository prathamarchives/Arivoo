-- 0014_reading_position.sql — P4-A slice two (CLAIM-066; PLAN's elaborated
-- P4-A slice two card; the #99 notverified's serving-generation routing;
-- record 58 §2): the source-open/position surface — the reserved surface
-- made real. The reading-position contract on the EXISTING substrate.
--
-- THE POSITION ROWS: owner+source scoped, keyed to the CURRENT generation
-- (THE SERVING-GENERATION FIELD: the position binds to the extraction
-- generation the reader was reading, so a re-extraction's answer is honest
-- about which generation the position addresses — never a silent retarget).
-- Append-only saves: a NEW immutable row per save (the (owner, source,
-- save_ordinal) identity — the bookmark revision shape); the read arm
-- derives the last-saved position (max ordinal) — never a state column
-- duplicating a derivable fact.
--
-- NO content column exists (the BMK-01 no-copy law: the structural pin);
-- the position is the owner's reading state — never shared, never inferred
-- (RLS scopes every row; the reader client is P4-B's separate repo).
--
-- Conventions (the 0004/0008/0009 substrate):
--   id/created_at: NO defaults — adapters/ids + adapters/clock (LAW-24)
--   owner_scope/actor/provenance (run_id, input_hash): NOT NULL (LAW-20/21)
--   RLS: app.current_owner scopes arv_app; arv_read = BYPASSRLS auditor (LAW-22)
--   append-only: UPDATE/DELETE refused (ARV-POS-005, the 0004 pattern)
--   THE SERIALIZED SAVE (the 0009 pattern): every insert takes the SAME
--     per-(owner, source) advisory xact lock the command takes (a
--     same-transaction re-acquisition is the no-op PostgreSQL defines, so
--     the command's own locked build never self-blocks)
--   THE ORDINAL LAW (ARV-POS-004): a save takes max(save_ordinal)+1 under
--     the lock — no skips, no collisions (the hostile-write backstop)
--   THE GENERATION-BIND LAW (ARV-POS-006): the serving-generation field
--     must name a generation OF THE SAME source in the caller's scope (a
--     position never binds a cross-source generation)
--
-- arv-baseline-bump: 2  (this file declares the guard triggers — procedural
-- constructs the fail-closed grammar cannot classify; AND it widens
-- arv.command_log.result_ref UUID -> TEXT — the position family's
-- user-coordinate result_ref <source>@<ordinal> is not a uuid. The widening
-- is the 0003 precedent class's honest extension: the replay answer's HOME
-- admits every command family's address form; every existing uuid row
-- widens to its canonical text form (idempotent under a re-run? NO — the
-- ALTER is guarded by a NOT NULL-preserving TYPE change that PostgreSQL
-- executes ONCE per database because the migration ledger runs each file
-- exactly once). The directive is the owner-visible paper trail.)

CREATE TABLE IF NOT EXISTS arv.reading_position (
    id              UUID        PRIMARY KEY,
    owner_scope     TEXT        NOT NULL,
    source_id       UUID        NOT NULL,
    save_ordinal    INTEGER     NOT NULL CHECK (save_ordinal >= 1),
    generation_id   UUID        NOT NULL,  -- THE SERVING-GENERATION FIELD: the generation current at save time
    start_off       INTEGER     NOT NULL CHECK (start_off >= 0),
    end_off         INTEGER     NOT NULL,
    actor           TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    run_id          TEXT        NOT NULL,
    input_hash      TEXT        NOT NULL,
    idempotency_key TEXT        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL,
    UNIQUE (id, owner_scope),
    UNIQUE (owner_scope, source_id, save_ordinal),  -- the ordinal law's substrate: one save per ordinal, ever
    FOREIGN KEY (source_id, owner_scope) REFERENCES arv.source (id, owner_scope),
    FOREIGN KEY (generation_id, owner_scope) REFERENCES arv.extraction_generation (id, owner_scope),
    CHECK (end_off > start_off)                     -- the location window is real, never inverted
);
-- the UNIQUE (owner_scope, source_id, save_ordinal) index serves the read
-- arm's max-ordinal derivation; no second index is declared (no list arm).

-- THE RESULT_REF WIDENING: arv.command_log.result_ref is the replay
-- answer's home for EVERY command family. The position family's answer is
-- the USER-COORDINATE address <source>@<ordinal> (the frozen ack grammar
-- POS-01 pins) — not a uuid. Every landed family's ref (a plain uuid text)
-- widens losslessly (uuid::text is its canonical form; the ack grammar
-- never changed). This is the column's own docstring kept honest: 'the
-- evidence row the command produced (the replay answer)' — the position's
-- evidence row IS reading_position@<ordinal>.
ALTER TABLE arv.command_log ALTER COLUMN result_ref TYPE TEXT;
-- any index depending on result_ref survives the TYPE change (PG rewrites
-- it); the sync bridge's typed join casts explicitly (harness/sync.py —
-- the ONE join that compares result_ref to a uuid column).
CREATE INDEX IF NOT EXISTS command_log_result_ref_idx
    ON arv.command_log (owner_scope, result_ref);

CREATE OR REPLACE FUNCTION arv.enforce_position_save_guard() RETURNS trigger AS $$
DECLARE
    nxt INTEGER;
    gen_src UUID;
BEGIN
    -- the serialized save (the 0009 pattern): the SAME advisory lock the
    -- command takes — hostile writers serialize behind it too
    PERFORM pg_advisory_xact_lock(hashtext(NEW.owner_scope || '|' || NEW.source_id::text));
    -- the ordinal law: a save takes max+1 under the lock (no skips, no collisions)
    SELECT COALESCE(max(save_ordinal), 0) INTO nxt
      FROM arv.reading_position
     WHERE source_id = NEW.source_id AND owner_scope = NEW.owner_scope;
    IF NEW.save_ordinal <> nxt + 1 THEN
        RAISE EXCEPTION 'ARV-POS-004: the position save ordinal % is not the next lawful save (% + 1) for source % — the ordinal law at the substrate (one save per ordinal, in order, under the serialized lock)', NEW.save_ordinal, nxt, NEW.source_id;
    END IF;
    -- the generation-bind law: the serving-generation field names a generation OF this source
    SELECT g.source_id INTO gen_src
      FROM arv.extraction_generation g
     WHERE g.id = NEW.generation_id AND g.owner_scope = NEW.owner_scope;
    IF gen_src IS NULL OR gen_src <> NEW.source_id THEN
        RAISE EXCEPTION 'ARV-POS-006: the position''s generation % is not a generation of source % — the serving-generation binding never crosses sources (the position addresses the generation the reader was reading)', NEW.generation_id, NEW.source_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS reading_position_save_guard ON arv.reading_position;
CREATE TRIGGER reading_position_save_guard
    BEFORE INSERT ON arv.reading_position
    FOR EACH ROW EXECUTE FUNCTION arv.enforce_position_save_guard();

CREATE OR REPLACE FUNCTION arv.reject_position_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'ARV-POS-005: arv.reading_position is append-only (id=%) — the reading-position history is authoritative state (the governed purge is the only erasure, D-011); the last-saved position is DERIVED (max ordinal), never a state column', OLD.id;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS reading_position_immutable ON arv.reading_position;
CREATE TRIGGER reading_position_immutable
    BEFORE UPDATE OR DELETE ON arv.reading_position
    FOR EACH ROW EXECUTE FUNCTION arv.reject_position_mutation();

ALTER TABLE arv.reading_position ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.reading_position FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS owner_isolation ON arv.reading_position;
CREATE POLICY owner_isolation ON arv.reading_position
    FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

GRANT INSERT, SELECT ON arv.reading_position TO arv_app;  -- NO UPDATE/DELETE: append-only
GRANT SELECT ON arv.reading_position TO arv_read;
