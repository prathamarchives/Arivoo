-- 0012_outbox.sql — P3-08 (CLAIM-059; RTM §3.4/§3.5 + SYS-08 + D-018/D-032):
-- the TWO outboxes. D-018's separation made mechanical: the CLIENT outbox
-- (offline durability + sync — the delivery state machine) and the SERVER
-- outbox (the post-commit enrichment handoff). Separate tables, separate
-- laws, never one mixed surface.
--
-- The client outbox (arv.outbox) is NOT append-only like the authoritative
-- tables: it is a STATE MACHINE (RTM §3.4) — but its delivery keys are
-- immutable after enqueue and its transitions follow the declared graph:
--   pending    -> delivered | retryable | failed
--   delivered  -> delivered | acknowledged | uncertain | retryable | failed
--   uncertain  -> delivered | acknowledged | retryable | failed
--   retryable  -> delivered | retryable | failed
--   acknowledged/failed: terminal (no outgoing edge)
-- DELETE is refused everywhere: the sync-intent audit trail is authoritative
-- state (RTM §4.4's export set names the outbox state; the governed purge is
-- the only erasure, D-011). acknowledged requires its server_ref (the ack
-- carries the server's own answer); a server_ref on any other state is a
-- lie about the server — refused.
--
-- The server outbox (arv.server_outbox) is strictly append-only at this
-- rung: the handoff ROW is the contract (atomic with the server-side
-- application); the enrichment consumers (P4+'s async rungs) amend the
-- state machine under their own slices. UPDATE and DELETE both refuse
-- (ARV-SYN-010).
--
-- arv-baseline-bump: 1  (this file declares the outbox guard triggers —
-- procedural constructs the fail-closed grammar cannot classify; the
-- directive is the owner-visible paper trail that admits them, per PLAN's
-- P3-M0 card / ARV-MIG-015, the 0003 precedent class.)

CREATE TABLE IF NOT EXISTS arv.outbox (
    owner_scope     TEXT        NOT NULL,
    seq             BIGINT      GENERATED ALWAYS AS IDENTITY,
    idempotency_key TEXT        NOT NULL,
    client_id       TEXT        NOT NULL,
    actor           TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    command_name    TEXT        NOT NULL,
    body_hash       TEXT        NOT NULL,
    payload         TEXT        NOT NULL,
    state           TEXT        NOT NULL CHECK (state IN ('pending','delivered','acknowledged','retryable','failed','uncertain')),
    attempts        INTEGER     NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    last_reason     TEXT,
    server_ref      TEXT,
    created_at      TIMESTAMPTZ NOT NULL,
    updated_at      TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (owner_scope, idempotency_key)
);
CREATE INDEX IF NOT EXISTS outbox_owner_seq ON arv.outbox (owner_scope, seq);

CREATE OR REPLACE FUNCTION arv.guard_outbox_state() RETURNS trigger AS $$
BEGIN
    IF NEW.owner_scope <> OLD.owner_scope OR NEW.seq <> OLD.seq
       OR NEW.idempotency_key <> OLD.idempotency_key OR NEW.client_id <> OLD.client_id
       OR NEW.actor <> OLD.actor OR NEW.command_name <> OLD.command_name
       OR NEW.body_hash <> OLD.body_hash OR NEW.payload <> OLD.payload
       OR NEW.created_at <> OLD.created_at THEN
        RAISE EXCEPTION 'ARV-SYN-004: the outbox row''s delivery keys are immutable after enqueue (owner=% key=%) — the sync intent never retargets; a different command is a different row', OLD.owner_scope, OLD.idempotency_key;
    END IF;
    IF NOT (
        (OLD.state = 'pending'   AND NEW.state IN ('delivered','retryable','failed'))
     OR (OLD.state = 'delivered' AND NEW.state IN ('delivered','acknowledged','uncertain','retryable','failed'))
     OR (OLD.state = 'uncertain' AND NEW.state IN ('delivered','acknowledged','retryable','failed'))
     OR (OLD.state = 'retryable' AND NEW.state IN ('delivered','retryable','failed'))
    ) THEN
        RAISE EXCEPTION 'ARV-SYN-005: the outbox transition % -> % is not in the declared state machine (RTM §3.4; key=%) — acknowledged and failed are terminal, and every edge is one of the declared graph', OLD.state, NEW.state, OLD.idempotency_key;
    END IF;
    IF NEW.attempts < OLD.attempts THEN
        RAISE EXCEPTION 'ARV-SYN-006: attempts may never decrease (key=%) — the retry count is the terminal policy''s own evidence', OLD.idempotency_key;
    END IF;
    IF (NEW.state = 'acknowledged' AND (NEW.server_ref IS NULL OR NEW.server_ref = ''))
       OR (NEW.state <> 'acknowledged' AND NEW.server_ref IS NOT NULL AND NEW.server_ref <> '') THEN
        RAISE EXCEPTION 'ARV-SYN-008: the server_ref law (key=%, state=%) — acknowledged requires the server''s recorded answer, and no other state may claim one', OLD.idempotency_key, NEW.state;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS outbox_state_guard ON arv.outbox;
CREATE TRIGGER outbox_state_guard
    BEFORE UPDATE ON arv.outbox
    FOR EACH ROW EXECUTE FUNCTION arv.guard_outbox_state();

CREATE OR REPLACE FUNCTION arv.reject_outbox_delete() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'ARV-SYN-007: DELETE on arv.outbox is refused — the sync-intent audit trail is authoritative state (RTM §4.4; the governed purge is the only erasure, D-011) — key=%', OLD.idempotency_key;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS outbox_no_delete ON arv.outbox;
CREATE TRIGGER outbox_no_delete
    BEFORE DELETE ON arv.outbox
    FOR EACH ROW EXECUTE FUNCTION arv.reject_outbox_delete();

ALTER TABLE arv.outbox ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.outbox FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS owner_isolation ON arv.outbox;
CREATE POLICY owner_isolation ON arv.outbox
    FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

GRANT INSERT, SELECT, UPDATE ON arv.outbox TO arv_app;
GRANT SELECT ON arv.outbox TO arv_read;

CREATE TABLE IF NOT EXISTS arv.server_outbox (
    owner_scope     TEXT        NOT NULL,
    idempotency_key TEXT        NOT NULL,
    command_name    TEXT        NOT NULL,
    body_hash       TEXT        NOT NULL,
    state           TEXT        NOT NULL DEFAULT 'pending' CHECK (state IN ('pending','enriched','failed')),
    created_at      TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (owner_scope, idempotency_key)
);

CREATE OR REPLACE FUNCTION arv.reject_server_outbox_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'ARV-SYN-010: arv.server_outbox is append-only at this rung (key=%) — the handoff row is the D-018 contract; the enrichment consumers amend the state machine under their own slices', OLD.idempotency_key;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS server_outbox_append_only ON arv.server_outbox;
CREATE TRIGGER server_outbox_append_only
    BEFORE UPDATE OR DELETE ON arv.server_outbox
    FOR EACH ROW EXECUTE FUNCTION arv.reject_server_outbox_mutation();

ALTER TABLE arv.server_outbox ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.server_outbox FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS owner_isolation ON arv.server_outbox;
CREATE POLICY owner_isolation ON arv.server_outbox
    FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

GRANT INSERT, SELECT ON arv.server_outbox TO arv_app;
GRANT SELECT ON arv.server_outbox TO arv_read;
