-- 0006_extraction_generations.sql — the P3-03a derived-state tables (RTM §2.3's
-- ExtractionGeneration contract + its passages; §3.6's derived-state pattern
-- instantiated for the extraction; SYS-06/07's primary trace). §2.9's DERIVED
-- class: disposable, rebuildable, NEVER authoritative — no unique authored
-- content lives only here; the authoritative Source row (0004) is always the
-- recovery substrate.
--
-- Conventions (the 0002/0003/0004 substrate, the disposable exception declared):
--   id/created_at/updated_at: NO defaults — adapters/ids + adapters/clock (LAW-24)
--   owner_scope/actor/provenance (run_id, input_hash): NOT NULL on every row (LAW-20/21)
--   RLS: app.current_owner scopes arv_app; arv_read = BYPASSRLS auditor (LAW-22)
--   NO append-only trigger — the generation tables are MUTABLE by design (the
--     §2.9 disposable exception, the 0005 precedent: building -> current/failed and
--     current -> superseded are LAWFUL UPDATEs, the state transition IS the machine)
--   NO command_log row is ever written for the extraction — a derived build is
--     never an owner command (§2.9); the idempotency record rides the generation
--     row itself: UNIQUE (owner_scope, idempotency_key), the body_hash conflict
--     guard beside it
--
-- The machine (the suite EXT-01..12 pins every transition):
--   (empty) --extract--> building           [the staging row, its OWN transaction]
--   building --complete generation--> current [passages + supersede + current, ONE transaction:
--                                              complete-or-failed publication — a partial
--                                              generation is never presented]
--   building --crash--> building            [persists; the same-key retry completes it; a
--                                              NEW-key extract supersedes it (the recovery)]
--   building --failure--> failed            [the named reason; the previous stays current]
--   current --new extraction, SAME source--> current(new) + superseded(old)  [both retained:
--                                              the versioned lineage, the ordinal per source]
--   a generation NEVER crosses source rows  [the edition bind: source_id is the version]

CREATE TABLE IF NOT EXISTS arv.extraction_generation (
    id               UUID        PRIMARY KEY,
    source_id        UUID        NOT NULL,
    ordinal          INTEGER     NOT NULL CHECK (ordinal >= 1),
    state            TEXT        NOT NULL CHECK (state IN ('building', 'current', 'failed', 'superseded')),
    extractor        TEXT        NOT NULL,  -- name+version, e.g. arivoo-text-blocks.v1
    extractor_config TEXT        NOT NULL,  -- the pinned config (the lineage's third field)
    input_digest     TEXT        NOT NULL,  -- the source's digest AT BUILD: the stale detector's substrate
    idempotency_key  TEXT        NOT NULL,
    body_hash        TEXT        NOT NULL,  -- the canonical command body hash (the 409 guard)
    fail_reason      TEXT        NULL,      -- the named code when state = 'failed'
    owner_scope      TEXT        NOT NULL,
    actor            TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    run_id           TEXT        NOT NULL,
    input_hash       TEXT        NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL,
    updated_at       TIMESTAMPTZ NOT NULL,
    UNIQUE (id, owner_scope),
    UNIQUE (source_id, ordinal),             -- the versioned lineage: one ordinal per source, ever
    UNIQUE (owner_scope, idempotency_key),   -- the derived-build idempotency record (never command_log)
    FOREIGN KEY (source_id, owner_scope) REFERENCES arv.source (id, owner_scope)
);
-- the ordinal is race-safe the same way the source edition is: concurrent same-source
-- extractions cannot both claim the ordinal (the loser's insert aborts — an honest
-- retry re-reads); a partial generation is never presented either way.
CREATE INDEX IF NOT EXISTS extraction_generation_source ON arv.extraction_generation (source_id, state, ordinal);
CREATE INDEX IF NOT EXISTS extraction_generation_owner  ON arv.extraction_generation (owner_scope, created_at, id);

CREATE TABLE IF NOT EXISTS arv.passage (
    id            UUID        PRIMARY KEY,
    generation_id UUID        NOT NULL,
    ordinal       INTEGER     NOT NULL CHECK (ordinal >= 1),
    start_off     INTEGER     NOT NULL CHECK (start_off >= 0),
    end_off       INTEGER     NOT NULL,
    text          TEXT        NOT NULL,     -- the exact slice of the decoded source text
    digest        TEXT        NOT NULL,     -- sha256 of the passage text: the re-hash check
    owner_scope   TEXT        NOT NULL,
    actor         TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    run_id        TEXT        NOT NULL,
    input_hash    TEXT        NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL,
    UNIQUE (id, owner_scope),
    UNIQUE (generation_id, ordinal),
    FOREIGN KEY (generation_id, owner_scope) REFERENCES arv.extraction_generation (id, owner_scope),
    CHECK (end_off > start_off)             -- the location evidence is real, never inverted
);
CREATE INDEX IF NOT EXISTS passage_generation ON arv.passage (generation_id, ordinal);
CREATE INDEX IF NOT EXISTS passage_owner      ON arv.passage (owner_scope, created_at, id);

ALTER TABLE arv.extraction_generation ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.extraction_generation FORCE ROW LEVEL SECURITY;
ALTER TABLE arv.passage ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.passage FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS owner_isolation ON arv.extraction_generation;
CREATE POLICY owner_isolation ON arv.extraction_generation FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));
DROP POLICY IF EXISTS owner_isolation ON arv.passage;
CREATE POLICY owner_isolation ON arv.passage FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

GRANT INSERT, SELECT, UPDATE ON arv.extraction_generation TO arv_app;  -- NO DELETE: rows transition,
GRANT INSERT, SELECT, UPDATE ON arv.passage TO arv_app;               -- the rebuild slice owns erasure
GRANT SELECT ON arv.extraction_generation TO arv_read;
GRANT SELECT ON arv.passage TO arv_read;
