-- 0013_purge_ledger.sql — P3-09 (CLAIM-060; RTM §3.7 + SYS-10 + D-029):
-- the governed purge/retention LEDGER. The permanence record: append-only
-- (a ledger entry can never be edited or deleted — D-029's purge/backup
-- expiry boundary and SYS-10's "a current-ledger entry WINS over older
-- archive content" both stand on this), owner-scoped, RLS-forced.
--
-- The GOVERNED PURGE COMMAND (the owner-facing erasure flow) is D-011's —
-- a later slice. This rung lands the LEDGER + the restore-time
-- reconciliation it powers: restore consults the DESTINATION's current
-- ledger FIRST and drops every ledgered entity from the archive's content
-- before declaring completion (an export made before a purge cannot
-- resurrect the purged item into a destination that carries the purge).
--
-- arv-baseline-bump: 1  (this file declares the append-only guard trigger —
-- a procedural construct the fail-closed grammar cannot classify; the
-- directive is the owner-visible paper trail, the 0003 precedent class.)

CREATE TABLE IF NOT EXISTS arv.purge_ledger (
    owner_scope TEXT        NOT NULL,
    kind        TEXT        NOT NULL CHECK (kind IN ('work','source','anchor','highlight','bookmark','note')),
    entity_id   UUID        NOT NULL,
    reason      TEXT        NOT NULL,
    actor       TEXT        NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (owner_scope, kind, entity_id)
);

CREATE OR REPLACE FUNCTION arv.reject_purge_ledger_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'ARV-PRG-001: arv.purge_ledger is append-only (owner=% kind=% entity=%) — the purge ledger IS the permanence record (D-029/SYS-10: a current entry wins over older archive content; an edited ledger would forge resurrection safety)', OLD.owner_scope, OLD.kind, OLD.entity_id;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS purge_ledger_append_only ON arv.purge_ledger;
CREATE TRIGGER purge_ledger_append_only
    BEFORE UPDATE OR DELETE ON arv.purge_ledger
    FOR EACH ROW EXECUTE FUNCTION arv.reject_purge_ledger_mutation();

ALTER TABLE arv.purge_ledger ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.purge_ledger FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS owner_isolation ON arv.purge_ledger;
CREATE POLICY owner_isolation ON arv.purge_ledger
    FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

-- The UPDATE grant is the LOCK ENABLER, never a mutation surface: the
-- restore's reconciliation transaction takes ACCESS EXCLUSIVE on this table
-- (serializing every concurrent ledger write against the reconciliation —
-- the SEV round-2 F1 repair), and PostgreSQL requires an UPDATE-class
-- privilege for that lock mode. THE APPEND-ONLY LAW IS THE TRIGGER
-- (ARV-PRG-001 fires for every role incl. the superuser): an UPDATE
-- statement by arv_app still refuses; the grant changes which LOCKS the
-- role may take, never which ROWS it may change.
GRANT INSERT, SELECT, UPDATE ON arv.purge_ledger TO arv_app;
GRANT SELECT ON arv.purge_ledger TO arv_read;
