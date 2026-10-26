-- 0005_import_journal.sql — the P3-02 staging journal (RTM §3.1's machine carrier;
-- §2.9's DISPOSABLE class: the recovery substrate for unfinished imports, never
-- authoritative owner data). The conventions per RTM §2 carry EXCEPT the one this
-- table exists to break: NO append-only trigger — the journal is MUTABLE by
-- design (staging -> staging_verified -> complete|failed are UPDATEs; the state
-- CHECK bounds the vocabulary; a failed import is retryable, and the same-key
-- retry rewinds its row through the ON CONFLICT upsert). The authoritative Source
-- row is BORN complete (§3.1: "the Source row + blob ref committed atomically") —
-- staging states exist ONLY here, never in arv.source (no phantom Source).
--
-- Conventions (the 0002/0003/0004 substrate, the disposable exception declared):
--   id/created_at/updated_at: NO defaults — adapters/ids + adapters/clock (LAW-24)
--   owner_scope/actor/provenance (run_id, input_hash): NOT NULL on every row (LAW-20/21)
--   RLS: app.current_owner scopes arv_app; arv_read = BYPASSRLS auditor (LAW-22)
--   Q11 baseline: no uniqueness on title/content — identity is the command's key
--
-- The re-drive contract: every field the metadata commit needs is recorded here
-- (work_id XOR title, digest, media_type, byte_size, acquired_via, client_id) plus
-- body_hash — the canonical command body hash. The recovery walk reconstructs the
-- canonical body FROM THESE FIELDS and hash-checks it against body_hash BEFORE
-- any re-drive (a mismatch is ARV-IMP-001, never a drive with an invented body).

CREATE TABLE IF NOT EXISTS arv.import_journal (
    id              UUID        PRIMARY KEY,
    owner_scope     TEXT        NOT NULL,
    actor           TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    idempotency_key TEXT        NOT NULL,
    client_id       TEXT        NOT NULL,
    work_id         UUID        NULL,   -- set for --work-id imports; NULL for --title rows
    title           TEXT        NULL,   -- set for --title imports; NULL for --work-id rows
    digest          TEXT        NOT NULL,
    media_type      TEXT        NOT NULL,
    byte_size       BIGINT      NOT NULL,
    acquired_via    TEXT        NOT NULL,
    state           TEXT        NOT NULL CHECK (state IN ('staging', 'staging_verified', 'complete', 'failed')),
    fail_reason     TEXT        NULL,   -- the named code when state = 'failed'
    source_id       UUID        NULL,   -- the committed source row, set at complete
    body_hash       TEXT        NOT NULL,
    run_id          TEXT        NOT NULL,
    input_hash      TEXT        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL,
    updated_at      TIMESTAMPTZ NOT NULL,
    UNIQUE (owner_scope, idempotency_key)  -- one journal row per command key: the re-drive finds it
);
CREATE INDEX IF NOT EXISTS import_journal_state ON arv.import_journal (owner_scope, state, created_at, id);

ALTER TABLE arv.import_journal ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.import_journal FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS owner_isolation ON arv.import_journal;
CREATE POLICY owner_isolation ON arv.import_journal FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

GRANT INSERT, SELECT, UPDATE ON arv.import_journal TO arv_app;  -- NO DELETE: rows transition, they are never erased
GRANT SELECT ON arv.import_journal TO arv_read;
