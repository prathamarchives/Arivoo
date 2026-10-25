-- 0003_command_log.sql — the idempotency ledger (S3; D-036).

-- arv-baseline-bump: 1  (P3-M0's admitted grammar: this file declares the plpgsql command-log
-- immutability trigger function — a procedural construct the fail-closed grammar cannot classify; the
-- directive is the owner-visible paper trail that admits it, per PLAN's P3-M0 card / ARV-MIG-015.)
--
-- The command registry's exactly-once substrate (LAW-23's pattern, early):
--   (owner_scope, idempotency_key) composite PK — per-owner keyspaces (LAW-22:
--     a global key would couple owners; B reusing A's key is a different command)
--   body_hash NOT NULL — same key + different body = the named conflict ARV-CMD-409
--   result_ref NOT NULL — the evidence row the command produced (the replay answer)
--   created_at NOT NULL, no default — the clock adapter supplies it (LAW-24)
--   append-only — the ARV-EV-002 trigger (an edited command log would corrupt
--     exactly-once; mutations are structurally impossible)

CREATE TABLE IF NOT EXISTS arv.command_log (
    owner_scope     TEXT        NOT NULL,
    idempotency_key TEXT        NOT NULL,
    client_id       TEXT        NOT NULL,
    command_name    TEXT        NOT NULL,
    body_hash       TEXT        NOT NULL,
    result_ref      UUID        NOT NULL,
    actor           TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    created_at      TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (owner_scope, idempotency_key)
);

CREATE OR REPLACE FUNCTION arv.reject_command_log_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'ARV-EV-002: the command log is immutable (LAW-23 substrate) — % on arv.command_log key=% rejected; the log IS the exactly-once record', TG_OP, OLD.idempotency_key;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS command_log_immutable ON arv.command_log;
CREATE TRIGGER command_log_immutable
    BEFORE UPDATE OR DELETE ON arv.command_log
    FOR EACH ROW EXECUTE FUNCTION arv.reject_command_log_mutation();

ALTER TABLE arv.command_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.command_log FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS owner_isolation ON arv.command_log;
CREATE POLICY owner_isolation ON arv.command_log
    FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

GRANT INSERT, SELECT ON arv.command_log TO arv_app;
GRANT SELECT ON arv.command_log TO arv_read;
