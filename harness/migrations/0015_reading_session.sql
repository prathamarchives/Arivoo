-- 0015_reading_session.sql — P4-C slice two (CLAIM-071; PLAN's elaborated
-- P4-C slice two card; the RTM §2.10 reservation: ReadingSession checkpoints
-- — behavior events INSIDE the D-010 boundary; record 63 §2): the
-- session/dwell events surface — D-010's durable behavior data.
--
-- THE EVENT ROWS: owner+source scoped, keyed to the CURRENT generation at
-- write time (THE SERVING-GENERATION BINDING the position surface
-- established: the event names the extraction generation the reader was
-- reading — the behavior history is PROVENANCE, never retargeted by a later
-- re-extraction). Append-only events (the 0014 shape): a NEW immutable row
-- per event (the (owner, source, event_ordinal) identity); the read arm
-- derives the listing — never a state column.
--
-- THE CLOSED VOCABULARY (D-010's boundary MADE STRUCTURAL): event IN
-- ('session_start', 'checkpoint', 'dwell', 'session_end') — coarse behavior
-- facts only. NO free-text column exists (the structural no-trace law: no
-- content/query/prompt/trace column — the row is coordinates + the coarse
-- dwell, never captured input). The CHECK below the command is the second
-- boundary: a hostile INSERT with an out-of-vocabulary kind (keystroke,
-- search_query, agent_prompt, ...) refuses at the substrate.
--
-- THE COARSE DWELL: dwell_ms only on 'dwell' events (the shape law), bounded
-- 1..86_400_000 ms (one day — a coarse measure, never a keystroke-level
-- trace; the bounds make the coarseness structural).
--
-- Conventions (the 0004/0008/0009/0014 substrate):
--   id/created_at: NO defaults — adapters/ids + adapters/clock (LAW-24)
--   owner_scope/actor/provenance (run_id, input_hash): NOT NULL (LAW-20/21)
--   RLS: app.current_owner scopes arv_app; arv_read = BYPASSRLS auditor (LAW-22)
--   append-only: UPDATE/DELETE refused (ARV-SES-006, the 0004 pattern)
--   THE SERIALIZED SAVE (the 0009 pattern): every insert takes the SAME
--     per-(owner, source) advisory xact lock the command takes
--   THE ORDINAL LAW (ARV-SES-007): an event takes max(event_ordinal)+1 under
--     the lock — no skips, no collisions (the hostile-write backstop)
--   THE GENERATION-BIND LAW (ARV-SES-008): the serving-generation field
--     must name a generation OF THE SAME source in the caller's scope
--
-- arv-baseline-bump: 2  (this file declares the guard triggers — procedural
-- constructs the fail-closed grammar cannot classify; NO existing table is
-- altered: the result_ref widening landed at 0014, and this family's
-- <source>@<ordinal> address rides the SAME TEXT column)

CREATE TABLE IF NOT EXISTS arv.reading_session (
    id              UUID        PRIMARY KEY,
    owner_scope     TEXT        NOT NULL,
    source_id       UUID        NOT NULL,
    event           TEXT        NOT NULL,
    event_ordinal   INTEGER     NOT NULL CHECK (event_ordinal >= 1),
    generation_id   UUID        NOT NULL,  -- THE SERVING-GENERATION BINDING: the generation current at event time
    start_off       INTEGER     NOT NULL CHECK (start_off >= 0),
    end_off         INTEGER     NOT NULL,
    dwell_ms        INTEGER,               -- NULL unless event = 'dwell' (the shape law below)
    actor           TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    run_id          TEXT        NOT NULL,
    input_hash      TEXT        NOT NULL,
    idempotency_key TEXT        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL,
    UNIQUE (id, owner_scope),
    UNIQUE (owner_scope, source_id, event_ordinal),  -- the ordinal law's substrate: one event per ordinal, ever
    FOREIGN KEY (source_id, owner_scope) REFERENCES arv.source (id, owner_scope),
    FOREIGN KEY (generation_id, owner_scope) REFERENCES arv.extraction_generation (id, owner_scope),
    CONSTRAINT reading_session_event_check
        CHECK (event IN ('session_start', 'checkpoint', 'dwell', 'session_end')),  -- D-010's closed vocabulary, structural
    CHECK (end_off > start_off),                     -- the coarse span is real, never inverted
    CHECK ((event = 'dwell' AND dwell_ms IS NOT NULL AND dwell_ms >= 1 AND dwell_ms <= 86400000)
           OR (event <> 'dwell' AND dwell_ms IS NULL))  -- the dwell shape + bounds law
);
-- the UNIQUE (owner_scope, source_id, event_ordinal) index serves the read
-- arm's per-source ordering; the listing orders by the event id (the keyset
-- convention every list arm rides).

CREATE OR REPLACE FUNCTION arv.enforce_session_event_guard() RETURNS trigger AS $$
DECLARE
    nxt INTEGER;
    gen_src UUID;
BEGIN
    -- the serialized save (the 0009 pattern): the SAME advisory lock the
    -- command takes — hostile writers serialize behind it too
    PERFORM pg_advisory_xact_lock(hashtext(NEW.owner_scope || '|' || NEW.source_id::text));
    -- the ordinal law: an event takes max+1 under the lock (no skips, no collisions)
    SELECT COALESCE(max(event_ordinal), 0) INTO nxt
      FROM arv.reading_session
     WHERE source_id = NEW.source_id AND owner_scope = NEW.owner_scope;
    IF NEW.event_ordinal <> nxt + 1 THEN
        RAISE EXCEPTION 'ARV-SES-007: the session event ordinal % is not the next lawful event (% + 1) for source % — the ordinal law at the substrate (one event per ordinal, in order, under the serialized lock)', NEW.event_ordinal, nxt, NEW.source_id;
    END IF;
    -- the generation-bind law: the serving-generation field names a generation OF this source
    SELECT g.source_id INTO gen_src
      FROM arv.extraction_generation g
     WHERE g.id = NEW.generation_id AND g.owner_scope = NEW.owner_scope;
    IF gen_src IS NULL OR gen_src <> NEW.source_id THEN
        RAISE EXCEPTION 'ARV-SES-008: the session event''s generation % is not a generation of source % — the serving-generation binding never crosses sources (the event names the generation the reader was reading)', NEW.generation_id, NEW.source_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS reading_session_save_guard ON arv.reading_session;
CREATE TRIGGER reading_session_save_guard
    BEFORE INSERT ON arv.reading_session
    FOR EACH ROW EXECUTE FUNCTION arv.enforce_session_event_guard();

CREATE OR REPLACE FUNCTION arv.reject_session_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'ARV-SES-006: arv.reading_session is append-only (id=%) — the behavior-event history is authoritative state (the governed purge is the only erasure, D-011); the listing is DERIVED, never a state column', OLD.id;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS reading_session_immutable ON arv.reading_session;
CREATE TRIGGER reading_session_immutable
    BEFORE UPDATE OR DELETE ON arv.reading_session
    FOR EACH ROW EXECUTE FUNCTION arv.reject_session_mutation();

ALTER TABLE arv.reading_session ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.reading_session FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS owner_isolation ON arv.reading_session;
CREATE POLICY owner_isolation ON arv.reading_session
    FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

GRANT INSERT, SELECT ON arv.reading_session TO arv_app;  -- NO UPDATE/DELETE: append-only
GRANT SELECT ON arv.reading_session TO arv_read;
