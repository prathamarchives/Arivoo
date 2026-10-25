-- 0004_p3_01_capture_skeleton.sql — the §1.6 capture skeleton (P3-01; RTM §2's
-- frozen shapes: work §2.1, source §2.2, anchor §2.4, highlight §2.5; D-041).

-- arv-baseline-bump: 1  (this file declares the shared plpgsql append-only guard —
-- a procedural construct P3-M0's fail-closed grammar cannot classify; the directive is
-- the owner-visible paper trail per PLAN's P3-M0 card / ARV-MIG-015.)

-- Conventions (RTM §2, the 0002/0003 substrate extended to the product entities):
--   id/created_at: NO defaults — adapters/ids + adapters/clock supply them (LAW-24)
--   owner_scope/actor/provenance (run_id, input_hash): NOT NULL on every row (LAW-20/21)
--   append-only: the ARV-CAP-005 trigger; revisions/tombstones are NEW rows (LAW-19)
--   RLS: app.current_owner scopes arv_app; arv_read = BYPASSRLS auditor (LAW-22)
--   Q11 baseline: NO uniqueness on work title/content — identity is the UUID only

CREATE TABLE IF NOT EXISTS arv.work (
    id          UUID        PRIMARY KEY,
    title       TEXT        NOT NULL,
    owner_scope TEXT        NOT NULL,
    actor       TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    run_id      TEXT        NOT NULL,
    input_hash  TEXT        NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL,
    UNIQUE (id, owner_scope)  -- the owner-scoped reference target (the SEV round's P2: FKs are owner-blind — composite FKs make every reference owner-consistent at the DB layer, closing the cross-owner plant and the FK-error existence oracle)
);

CREATE TABLE IF NOT EXISTS arv.source (
    id              UUID        PRIMARY KEY,
    work_id         UUID        NOT NULL,
    digest          TEXT        NOT NULL,
    media_type      TEXT        NOT NULL,
    byte_size       BIGINT      NOT NULL,
    blob_ref        TEXT        NOT NULL,
    acquired_via    TEXT        NOT NULL,
    import_state    TEXT        NOT NULL CHECK (import_state IN ('staging', 'staging_verified', 'complete', 'failed')),
    source_version  INTEGER     NOT NULL CHECK (source_version >= 1),
    owner_scope     TEXT        NOT NULL,
    actor           TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    run_id          TEXT        NOT NULL,
    input_hash      TEXT        NOT NULL,
    idempotency_key TEXT        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL,
    UNIQUE (id, owner_scope),
    FOREIGN KEY (work_id, owner_scope) REFERENCES arv.work (id, owner_scope)
);
CREATE INDEX IF NOT EXISTS source_owner ON arv.source (owner_scope, created_at);
CREATE INDEX IF NOT EXISTS source_work  ON arv.source (work_id, source_version);
-- The edition ordinal is race-safe: concurrent same-work imports cannot both
-- claim the same version (the loser's insert aborts — an honest retry re-reads).
CREATE UNIQUE INDEX IF NOT EXISTS source_work_version ON arv.source (work_id, source_version);

-- The Anchor (RTM §2.4): the durable pointer INTO a specific Source version.
-- source_digest IS the version tie; offsets are UTF-8 character offsets into
-- the decoded text (the pinned P3-01 choice for text/* — the format-appropriate
-- location evidence); the context slices are the fallback matching evidence.
CREATE TABLE IF NOT EXISTS arv.anchor (
    id             UUID        PRIMARY KEY,
    source_id      UUID        NOT NULL,
    source_digest  TEXT        NOT NULL,
    start_off      INTEGER     NOT NULL,
    end_off        INTEGER     NOT NULL,
    context_before TEXT        NOT NULL,
    context_after TEXT        NOT NULL,
    media_type     TEXT        NOT NULL,
    owner_scope    TEXT        NOT NULL,
    actor          TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    run_id         TEXT        NOT NULL,
    input_hash     TEXT        NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL,
    CHECK (end_off > start_off),
    UNIQUE (id, owner_scope),
    FOREIGN KEY (source_id, owner_scope) REFERENCES arv.source (id, owner_scope)
);

-- The Highlight (RTM §2.5): stable UUID identity + append-only revisions.
-- P3-01 mints revision 1 only; the revision/tombstone machine (§3.3) is P3-04's.
-- idempotency_key = the command-log row's key (the command provenance ref).
CREATE TABLE IF NOT EXISTS arv.highlight (
    id              UUID        NOT NULL,
    revision        INTEGER     NOT NULL CHECK (revision >= 1),
    selected_text   TEXT        NOT NULL,
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
    FOREIGN KEY (anchor_id, owner_scope) REFERENCES arv.anchor (id, owner_scope)
);
CREATE INDEX IF NOT EXISTS highlight_owner ON arv.highlight (owner_scope, created_at);

CREATE OR REPLACE FUNCTION arv.reject_capture_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'ARV-CAP-005: % on %.% is refused — authoritative rows are append-only (revisions and tombstones are NEW rows; the owner-run purge is the only authorized erasure, D-011)', TG_OP, TG_TABLE_SCHEMA, TG_TABLE_NAME;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS work_immutable ON arv.work;
CREATE TRIGGER work_immutable BEFORE UPDATE OR DELETE ON arv.work
    FOR EACH ROW EXECUTE FUNCTION arv.reject_capture_mutation();
DROP TRIGGER IF EXISTS source_immutable ON arv.source;
CREATE TRIGGER source_immutable BEFORE UPDATE OR DELETE ON arv.source
    FOR EACH ROW EXECUTE FUNCTION arv.reject_capture_mutation();
DROP TRIGGER IF EXISTS anchor_immutable ON arv.anchor;
CREATE TRIGGER anchor_immutable BEFORE UPDATE OR DELETE ON arv.anchor
    FOR EACH ROW EXECUTE FUNCTION arv.reject_capture_mutation();
DROP TRIGGER IF EXISTS highlight_immutable ON arv.highlight;
CREATE TRIGGER highlight_immutable BEFORE UPDATE OR DELETE ON arv.highlight
    FOR EACH ROW EXECUTE FUNCTION arv.reject_capture_mutation();

ALTER TABLE arv.work    ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.work    FORCE ROW LEVEL SECURITY;
ALTER TABLE arv.source  ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.source  FORCE ROW LEVEL SECURITY;
ALTER TABLE arv.anchor  ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.anchor  FORCE ROW LEVEL SECURITY;
ALTER TABLE arv.highlight ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.highlight FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS owner_isolation ON arv.work;
CREATE POLICY owner_isolation ON arv.work FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));
DROP POLICY IF EXISTS owner_isolation ON arv.source;
CREATE POLICY owner_isolation ON arv.source FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));
DROP POLICY IF EXISTS owner_isolation ON arv.anchor;
CREATE POLICY owner_isolation ON arv.anchor FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));
DROP POLICY IF EXISTS owner_isolation ON arv.highlight;
CREATE POLICY owner_isolation ON arv.highlight FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

GRANT INSERT, SELECT ON arv.work, arv.source, arv.anchor, arv.highlight TO arv_app;
GRANT SELECT ON arv.work, arv.source, arv.anchor, arv.highlight TO arv_read;
