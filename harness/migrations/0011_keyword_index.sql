-- 0011_keyword_index.sql — P3-07 (CLAIM-058; RTM §2.5 the findability rung,
-- C1's durability ladder lands keyword-searchable): the REBUILDABLE keyword
-- index. THE DERIVED-LAYER LAW: this table is the one NON-authoritative
-- store — tokens + locators only (NO authored content column), re-derivable
-- from the authored rows alone (the rebuild command; the acceptance pin),
-- droppable with zero authored effect. arv_app holds DELETE here by design
-- (SYS-07: the derived index CARRIES processing/input provenance — the
-- extractor identity + config + the indexed text's digest, the 0006
-- extraction-generation convention applied to the keyword rung)
-- (the rebuild's own surface: delete + re-derive) — the grant is the
-- derived-layer law made mechanical. Visibility is NEVER governed here: the
-- search arm joins the authoritative current-view parity (tombstones
-- filtered at QUERY time); the index holds the CURRENT revisions' tokens.
CREATE TABLE IF NOT EXISTS arv.keyword_index (
    owner_scope     TEXT        NOT NULL,
    kind            TEXT        NOT NULL CHECK (kind IN ('source', 'highlight', 'bookmark', 'note')),
    entity_id       UUID        NOT NULL,
    revision        INTEGER     NOT NULL CHECK (revision >= 1),
    token           TEXT        NOT NULL,
    extractor       TEXT        NOT NULL,
    extractor_config TEXT       NOT NULL,
    input_digest    TEXT        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (owner_scope, kind, entity_id, revision, token)
);
CREATE INDEX IF NOT EXISTS keyword_index_token ON arv.keyword_index (owner_scope, token, kind, entity_id);

ALTER TABLE arv.keyword_index ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.keyword_index FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS owner_isolation ON arv.keyword_index;
CREATE POLICY owner_isolation ON arv.keyword_index FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

GRANT INSERT, DELETE, SELECT ON arv.keyword_index TO arv_app;
GRANT SELECT ON arv.keyword_index TO arv_read;
