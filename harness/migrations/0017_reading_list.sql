-- 0017_reading_list.sql — P4-C slice five (CLAIM-074; PLAN's elaborated P4-C
-- slice five card; record 66 §2): the reading-list surface — the user-defined
-- lists over the landed library (the North Star owner words' third surface:
-- "I have lists, a library, and lists of what I'm currently reading" — the
-- library and the current-reading lists LANDED at CLAIM-070, the LISTS here).
--
-- THE LIST HEADER (arv.reading_list): append-only, owner-scoped, the
-- single-row family shape (UNIQUE (id, owner_scope), the 0015 pattern — a
-- list is ONE identity, not a revision table; the name is IMMUTABLE at this
-- slice: a rename is its own increment). The name is the owner's own label,
-- 1..512 chars — NO uniqueness over names (Q11's identity baseline: the
-- identity is the uuid, NEVER the name; two lists may share a name — no
-- auto-merge, no identity uniqueness assumptions).
--
-- THE MEMBERSHIP EVENT ROWS (arv.reading_list_member): the append-only
-- history — every add/remove is a NEW event row (the closed op vocabulary
-- 'added'|'removed', the 0015/0016 closed-vocabulary pattern). The CURRENT
-- membership is DERIVED: the last op per (list, source) wins — a projection;
-- the event rows are the recovery substrate (RTM §2 item 9's derived-state
-- rule: every add/remove retained, never a destructive delete, the full
-- history reconstructable from the events alone).
--
-- THE ALTERNATION LAW (ARV-RLS-008, the insert guard): an 'added' event
-- requires the pair's current state to differ (a double-add is a phantom);
-- a 'removed' event likewise. The guard takes the per-pair advisory xact
-- lock (the 0009 serialized pattern: hashtext(list || ':' || source) — ONE
-- key form, hostile writers serialize behind the command path). The command
-- layer's own idempotency (the spine's key semantics) never double-inserts;
-- the guard is the structural law against direct hostile writes.
--
-- Conventions (the 0004/0009/0014/0015/0016 substrate):
--   id/created_at: NO defaults — adapters/ids + adapters/clock (LAW-24)
--   owner_scope/actor/provenance (run_id, input_hash): NOT NULL (LAW-20/21)
--   RLS: app.current_owner scopes arv_app; arv_read = BYPASSRLS auditor (LAW-22)
--   append-only: UPDATE/DELETE refused (ARV-RLS-006 the header, ARV-RLS-007
--     the events — the 0004 pattern)
--   the composite FKs: (list_id, owner_scope) and (source_id, owner_scope)
--     make both references owner-consistent at the DB layer (the 0004 law)
--
-- arv-baseline-bump: 2  (this file declares the guard trigger — a procedural
-- construct the fail-closed grammar cannot classify; NO existing table is
-- altered)

CREATE TABLE IF NOT EXISTS arv.reading_list (
    id              UUID        NOT NULL,
    name            TEXT        NOT NULL
                    CONSTRAINT reading_list_name_check
                    CHECK (length(name) BETWEEN 1 AND 512),  -- the owner's own label; the NUL law is the command's ARV-RLS-003
    owner_scope     TEXT        NOT NULL,
    actor           TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    run_id          TEXT        NOT NULL,
    input_hash      TEXT        NOT NULL,
    idempotency_key TEXT        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL,
    UNIQUE (id, owner_scope)    -- the single-row family shape (the 0015 pattern)
);
-- NO uniqueness over names — Q11's identity baseline: the identity is the
-- uuid, never the name; two lists may share one name (no auto-merge).

CREATE TABLE IF NOT EXISTS arv.reading_list_member (
    id              UUID        NOT NULL,
    list_id         UUID        NOT NULL,
    source_id       UUID        NOT NULL,
    op              TEXT        NOT NULL
                    CONSTRAINT reading_list_member_op_check
                    CHECK (op IN ('added', 'removed')),  -- the closed op vocabulary, structural
    owner_scope     TEXT        NOT NULL,
    actor           TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    run_id          TEXT        NOT NULL,
    input_hash      TEXT        NOT NULL,
    idempotency_key TEXT        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL,
    UNIQUE (id, owner_scope),   -- the event identity (the single-row family shape)
    FOREIGN KEY (list_id, owner_scope) REFERENCES arv.reading_list (id, owner_scope),
    FOREIGN KEY (source_id, owner_scope) REFERENCES arv.source (id, owner_scope)
);
-- the current membership is DERIVED (the last op per pair wins); the event
-- rows are the authoritative history — never a state column to mutate.

CREATE OR REPLACE FUNCTION arv.enforce_reading_list_member_guard() RETURNS trigger AS $$
DECLARE
    cur TEXT;
BEGIN
    -- the serialized pair (the 0009 pattern): ONE advisory key per
    -- (list, source) — hostile writers serialize behind the command path
    PERFORM pg_advisory_xact_lock(hashtext(NEW.list_id::text || ':' || NEW.source_id::text));
    -- the alternation law (ARV-RLS-008): an event's op must differ from the
    -- pair's current state — a double-add or a double-remove is a phantom
    SELECT op INTO cur FROM arv.reading_list_member
        WHERE list_id = NEW.list_id AND source_id = NEW.source_id
          AND owner_scope = NEW.owner_scope
        ORDER BY created_at DESC, id DESC LIMIT 1;
    IF cur IS NOT DISTINCT FROM NEW.op THEN
        RAISE EXCEPTION 'ARV-RLS-008: the membership event op % for list % source % duplicates the pair''s current state — membership events ALTERNATE (added|removed, the append-only history; the current view derives from the last op)', NEW.op, NEW.list_id, NEW.source_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS reading_list_member_guard ON arv.reading_list_member;
CREATE TRIGGER reading_list_member_guard BEFORE INSERT ON arv.reading_list_member
    FOR EACH ROW EXECUTE FUNCTION arv.enforce_reading_list_member_guard();

CREATE OR REPLACE FUNCTION arv.reject_reading_list_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'ARV-RLS-006: % on %.% is refused — the reading-list header is append-only (the name immutable at this slice; the governed purge is the only authorized erasure, D-011)', TG_OP, TG_TABLE_SCHEMA, TG_TABLE_NAME;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS reading_list_immutable ON arv.reading_list;
CREATE TRIGGER reading_list_immutable BEFORE UPDATE OR DELETE ON arv.reading_list
    FOR EACH ROW EXECUTE FUNCTION arv.reject_reading_list_mutation();

CREATE OR REPLACE FUNCTION arv.reject_reading_list_member_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'ARV-RLS-007: % on %.% is refused — the membership event history is append-only authoritative state (the current view is DERIVED, never a state column; the governed purge is the only erasure, D-011)', TG_OP, TG_TABLE_SCHEMA, TG_TABLE_NAME;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS reading_list_member_immutable ON arv.reading_list_member;
CREATE TRIGGER reading_list_member_immutable BEFORE UPDATE OR DELETE ON arv.reading_list_member
    FOR EACH ROW EXECUTE FUNCTION arv.reject_reading_list_member_mutation();

ALTER TABLE arv.reading_list ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.reading_list FORCE ROW LEVEL SECURITY;
ALTER TABLE arv.reading_list_member ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.reading_list_member FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS owner_isolation ON arv.reading_list;
CREATE POLICY owner_isolation ON arv.reading_list FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

DROP POLICY IF EXISTS owner_isolation ON arv.reading_list_member;
CREATE POLICY owner_isolation ON arv.reading_list_member FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

GRANT INSERT, SELECT ON arv.reading_list TO arv_app;   -- NO UPDATE/DELETE: append-only
GRANT SELECT ON arv.reading_list TO arv_read;
GRANT INSERT, SELECT ON arv.reading_list_member TO arv_app;
GRANT SELECT ON arv.reading_list_member TO arv_read;
