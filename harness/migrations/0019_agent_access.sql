-- 0019_agent_access.sql — P4-E SLICE ONE (CLAIM-077; record 69 §2): the scoped
-- agent read surface's substrate — the owner-minted credential + the append-only
-- read audit. The PLAN 4E row: "authorized agents read the owner's journal and
-- capture context through the same API with provenance/scope/budgets; READ-ONLY
-- at first; owner-scope enforced on every query; no arbitrary database access;
-- Q9/Q10 handled honestly."
--
-- THE CREDENTIAL (arv.agent_credential): the owner-minted authorization — the
-- token VALUE generated at 32 bytes secrets-quality randomness, shown ONCE in
-- the mint ack (the password-reset convention), ONLY the sha256 stored (the
-- value never persisted, never logged); the closed scopes CHECK (scopes =
-- 'read' — READ-ONLY structural, the row's own letter); the ONE-WAY revocation
-- (revoked_at NULL -> set, never unset — the guarded one-transition law; the
-- alternation refuses the already-revoked, the purge's own finality class).
-- NO outbox ride: the credential is a LOCAL access primitive, never owner
-- content to replicate.
--
-- THE AUDIT TRAIL (arv.agent_read_log): append-only, one row per SERVED agent
-- read — the credential + the arm + the bounded REQUEST facts (the page limit
-- and the keyset cursor), NEVER the content (a read log that stored what was
-- read would be a second copy of the library — the structural no-content law).
--
-- THE VERIFICATION FUNCTION (arv.agent_token_lookup): the narrow SECURITY
-- DEFINER primitive — the sha256 lookup WITHOUT a prior owner scope (the
-- chicken-and-egg: the scope comes FROM the credential). The definer (the
-- migration runner, the superuser) bypasses the forced RLS; the function
-- exposes ONLY the (owner_scope, credential_id) pair for a LIVE 'read'-scoped
-- credential — nothing else, never the label, never the log. This is the
-- system's own authentication step, never an agent-reachable arbitrary read
-- (the "no arbitrary database access" law is about the agent's READS, all of
-- which ride the RLS-scoped arms).
--
-- arv-baseline-bump: 1  (the one-transition guard + the verification function
-- are procedural constructs the admitted grammar cannot classify — the
-- 0004/0010 convention, the owner-visible paper trail)
CREATE TABLE IF NOT EXISTS arv.agent_credential (
    id              UUID PRIMARY KEY,
    owner_scope     TEXT        NOT NULL,
    label           TEXT        NOT NULL CHECK (char_length(label) BETWEEN 1 AND 128),  -- the NUL law is the command's ARV-AGT-003 (the 0017 convention: chr(0) itself is illegal in PG text)
    token_hash      TEXT        NOT NULL CHECK (token_hash ~ '^[0-9a-f]{64}$'),
    scopes          TEXT        NOT NULL CHECK (scopes = 'read'),
    actor           TEXT        NOT NULL CHECK (actor IN ('owner', 'runtime-agent', 'worker', 'model-decision')),
    run_id          TEXT        NOT NULL,
    input_hash      TEXT        NOT NULL,
    idempotency_key TEXT        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL,
    revoked_at      TIMESTAMPTZ,
    UNIQUE (id, owner_scope)
);

-- the one-transition guard: revoked_at is the ONLY mutable column, NULL -> set,
-- never back; every other column immutable; DELETE always refused (the append-
-- only substrate family's reject function, DELETE-only here — the UPDATE path
-- is the guarded transition's own)
CREATE OR REPLACE FUNCTION arv.guard_agent_credential() RETURNS trigger AS $$
BEGIN
    IF NEW.id <> OLD.id OR NEW.owner_scope <> OLD.owner_scope
       OR NEW.label <> OLD.label OR NEW.token_hash <> OLD.token_hash
       OR NEW.scopes <> OLD.scopes OR NEW.created_at <> OLD.created_at
       OR NEW.actor <> OLD.actor OR NEW.run_id <> OLD.run_id
       OR NEW.input_hash <> OLD.input_hash OR NEW.idempotency_key <> OLD.idempotency_key THEN
        RAISE EXCEPTION 'ARV-AGT-004: the credential is immutable except the one-way revocation — only revoked_at may change, from NULL to set, never back';
    END IF;
    IF OLD.revoked_at IS NOT NULL THEN
        RAISE EXCEPTION 'ARV-AGT-004: the credential is already revoked — the revocation is final (mint a new credential if access is wanted again)';
    END IF;
    IF NEW.revoked_at IS NULL THEN
        RAISE EXCEPTION 'ARV-AGT-004: the revocation is one-way — revoked_at cannot be cleared once set';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS agent_credential_guard ON arv.agent_credential;
CREATE TRIGGER agent_credential_guard BEFORE UPDATE ON arv.agent_credential
    FOR EACH ROW EXECUTE FUNCTION arv.guard_agent_credential();

DROP TRIGGER IF EXISTS agent_credential_immutable ON arv.agent_credential;
CREATE TRIGGER agent_credential_immutable BEFORE DELETE ON arv.agent_credential
    FOR EACH ROW EXECUTE FUNCTION arv.reject_capture_mutation();

CREATE TABLE IF NOT EXISTS arv.agent_read_log (
    id              UUID PRIMARY KEY,
    credential_id   UUID        NOT NULL,
    owner_scope     TEXT        NOT NULL,
    arm             TEXT        NOT NULL CHECK (char_length(arm) BETWEEN 1 AND 64),  -- the arm names are the parser's own closed set, never caller text
    req_limit       INTEGER,
    req_after       TEXT,
    created_at      TIMESTAMPTZ NOT NULL,
    UNIQUE (id, owner_scope)
);
CREATE INDEX IF NOT EXISTS agent_read_log_cred
    ON arv.agent_read_log (credential_id, created_at, id);

DROP TRIGGER IF EXISTS agent_read_log_immutable ON arv.agent_read_log;
CREATE TRIGGER agent_read_log_immutable BEFORE UPDATE OR DELETE ON arv.agent_read_log
    FOR EACH ROW EXECUTE FUNCTION arv.reject_capture_mutation();

-- the narrow verification primitive (the SECURITY DEFINER lookup — see the
-- header's design note): sha256 -> the live 'read'-scoped credential's scope
CREATE OR REPLACE FUNCTION arv.agent_token_lookup(p_token_hash TEXT)
RETURNS TABLE (owner_scope TEXT, credential_id UUID) AS $$
    SELECT c.owner_scope, c.id
    FROM arv.agent_credential c
    WHERE c.token_hash = p_token_hash
      AND c.revoked_at IS NULL
      AND c.scopes = 'read';
$$ LANGUAGE sql SECURITY DEFINER SET search_path = pg_catalog, arv;

ALTER TABLE arv.agent_credential ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.agent_credential FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS owner_isolation ON arv.agent_credential;
CREATE POLICY owner_isolation ON arv.agent_credential FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

ALTER TABLE arv.agent_read_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.agent_read_log FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS owner_isolation ON arv.agent_read_log;
CREATE POLICY owner_isolation ON arv.agent_read_log FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

-- the grants: INSERT + SELECT for the mint and the reads; UPDATE for the ONE
-- guarded transition (the trigger is the law — the 0007/0008 convention: both
-- layers, never one alone); the read log INSERT + SELECT only
GRANT INSERT, SELECT, UPDATE ON arv.agent_credential TO arv_app;
GRANT SELECT ON arv.agent_credential TO arv_read;
GRANT INSERT, SELECT ON arv.agent_read_log TO arv_app;
GRANT SELECT ON arv.agent_read_log TO arv_read;
-- F-077-2 (the SEV round-1 repair): PostgreSQL grants EXECUTE on functions to
-- PUBLIC by default — the "narrow lookup" letter requires the explicit
-- revocation (arv_read resolving a live hash observed live by the reviewer;
-- the impact bounded — the caller needs the 190-bit hash — but the letter
-- must hold)
REVOKE EXECUTE ON FUNCTION arv.agent_token_lookup(TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION arv.agent_token_lookup(TEXT) TO arv_app;
