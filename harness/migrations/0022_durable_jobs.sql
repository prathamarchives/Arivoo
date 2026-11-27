-- 0022_durable_jobs.sql — CLAIM-104 (Workstream 9; runbook §12.1/§12.2; the directive's
-- durable-workers workstream): the JOB QUEUE substrate.
--
-- The design (the runbook's own requirements, mechanical):
--   * arv.job — the durable job record: id, owner scope, job type (the closed
--     vocabulary of the landed async work: extract_source, rebuild_keyword_index,
--     recovery_walk, rebuild_derived), payload schema version, idempotency/dedupe
--     key (UNIQUE per owner+type — duplicate submissions converge), small
--     validated payload (the owner-scoped object references only — never whole
--     documents, §12.3's law), state, attempt count, available_after (the
--     backoff clock), lease_owner + lease_expires_at (the lease), the MONOTONIC
--     fencing token (granted per lease acquisition), the last typed error,
--     created/updated/completed timestamps.
--   * the states (§12.1): queued -> leased -> succeeded | retryable -> leased... |
--     dead (the terminal poison class — one poison job never blocks the queue);
--     succeeded/dead are terminal.
--   * THE CLAIM (§12.2): one atomic statement — SELECT ... FOR UPDATE SKIP LOCKED
--     over the due rows (state IN (queued, retryable) AND available_after <= now),
--     the lease + the fencing token granted in the SAME transaction (token =
--     a per-row monotonic counter — every lease grant increments; a stale worker's
--     completion names an OLD token and the completion guard refuses it: a stale
--     worker must not complete a job after another worker reclaimed it).
--   * THE FENCING GUARD: the completion (succeeded/dead/retryable-with-error)
--     UPDATE carries WHERE id = X AND fencing_token = T AND lease_owner = W —
--     a token mismatch means the lease was reclaimed; the stale worker's write
--     matches ZERO rows and it observes the loss (the honest answer, never a
--     double-complete).
--   * NO content in the log-ish surfaces: the typed error is a code + a bounded
--     message (never source contents, never secrets — §11.4's law).
--
-- arv-baseline-bump: 1  (the claim is a procedural construct — the SKIP LOCKED
-- claim function + the fencing guard are the fail-closed grammar's named class;
-- the 0012/0019 convention, the owner-visible paper trail)

CREATE TABLE IF NOT EXISTS arv.job (
    id                 UUID        PRIMARY KEY,
    owner_scope        TEXT        NOT NULL,
    job_type           TEXT        NOT NULL CHECK (job_type IN
                                     ('extract_source', 'rebuild_keyword_index',
                                      'recovery_walk', 'rebuild_derived')),
    payload_version    INTEGER     NOT NULL CHECK (payload_version = 1),
    payload            JSONB       NOT NULL,
    idem_key           TEXT        NOT NULL,
    state              TEXT        NOT NULL CHECK (state IN
                                     ('queued', 'leased', 'succeeded',
                                      'retryable', 'dead')),
    attempts           INTEGER     NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    available_after    TIMESTAMPTZ NOT NULL DEFAULT now(),
    lease_owner        TEXT,
    lease_expires_at   TIMESTAMPTZ,
    fencing_token      BIGINT      NOT NULL DEFAULT 0,
    last_error         TEXT,
    created_at         TIMESTAMPTZ NOT NULL,
    updated_at         TIMESTAMPTZ NOT NULL,
    completed_at       TIMESTAMPTZ,
    UNIQUE (owner_scope, job_type, idem_key)  -- the dedupe: duplicate submissions converge
);
CREATE INDEX IF NOT EXISTS job_due ON arv.job (state, available_after);

ALTER TABLE arv.job ENABLE ROW LEVEL SECURITY;
ALTER TABLE arv.job FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS job_owner_isolation ON arv.job;
CREATE POLICY job_owner_isolation ON arv.job FOR ALL TO arv_app
    USING (owner_scope = current_setting('app.current_owner', true))
    WITH CHECK (owner_scope = current_setting('app.current_owner', true));

-- THE CLAIM: the atomic lease acquisition (SKIP LOCKED — one claimant per row;
-- the expired lease is RECLAIMABLE: a leased row past lease_expires_at is due
-- again, the fencing token increments, the stale holder's completion refuses)
CREATE OR REPLACE FUNCTION arv.job_claim(
    p_worker TEXT, p_limit INTEGER, p_lease_seconds INTEGER)
RETURNS TABLE (id UUID, owner_scope TEXT, job_type TEXT, payload JSONB,
               fencing_token BIGINT, attempts INTEGER) AS $$
    WITH due AS (
        SELECT j.id FROM arv.job j
        WHERE (j.state IN ('queued', 'retryable') AND j.available_after <= now())
           OR (j.state = 'leased' AND j.lease_expires_at <= now())
        ORDER BY j.available_after, j.id
        LIMIT GREATEST(1, LEAST(p_limit, 10))
        FOR UPDATE SKIP LOCKED
    )
    UPDATE arv.job j
    SET state = 'leased', lease_owner = p_worker,
        lease_expires_at = now() + make_interval(secs => GREATEST(1, p_lease_seconds)),
        fencing_token = 1 + j.fencing_token,
        attempts = j.attempts + 1,
        updated_at = now()
    FROM due
    WHERE j.id = due.id
    RETURNING j.id, j.owner_scope, j.job_type, j.payload, j.fencing_token, j.attempts;
$$ LANGUAGE sql SECURITY DEFINER SET search_path = pg_catalog, arv;

-- THE FENCED COMPLETION: succeeded / dead / retryable-with-error — every form
-- carries the fencing predicate; a stale worker's write matches ZERO rows and
-- the function answers 'lost' (the honest observation, never a double-complete)
CREATE OR REPLACE FUNCTION arv.job_complete(
    p_id UUID, p_worker TEXT, p_token BIGINT, p_outcome TEXT, p_error TEXT)
RETURNS TEXT AS $$
DECLARE
    v_rows INTEGER;
BEGIN
    IF p_outcome NOT IN ('succeeded', 'dead', 'retryable') THEN
        RAISE EXCEPTION 'ARV-JOB-002: the outcome must be succeeded|dead|retryable (the closed vocabulary — never a guessed state)';
    END IF;
    UPDATE arv.job SET
        state = p_outcome,
        lease_owner = NULL, lease_expires_at = NULL,
        last_error = CASE WHEN p_outcome = 'succeeded' THEN NULL
                          ELSE left(coalesce(p_error, 'the unnamed typed error'), 512) END,
        available_after = CASE WHEN p_outcome = 'retryable'
                                THEN now() + make_interval(secs => 30 * GREATEST(1, attempts))
                                ELSE available_after END,
        completed_at = CASE WHEN p_outcome IN ('succeeded', 'dead') THEN now()
                            ELSE NULL END,
        updated_at = now()
    WHERE id = p_id AND lease_owner = p_worker AND fencing_token = p_token
      AND state = 'leased';
    GET DIAGNOSTICS v_rows = ROW_COUNT;
    IF v_rows = 0 THEN
        RETURN 'lost';  -- the lease was reclaimed (or completed elsewhere): the
                        -- stale worker observes its loss — never a double-complete
    END IF;
    RETURN 'ok';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, arv;

-- the poison policy: attempts >= 8 on a retryable outcome goes dead (the
-- terminal class; one poison job never blocks the queue — it is answered,
-- visible, and final)
CREATE OR REPLACE FUNCTION arv.job_poison_guard() RETURNS trigger AS $$
BEGIN
    IF NEW.state = 'retryable' AND NEW.attempts >= 8 THEN
        NEW.state := 'dead';
        NEW.completed_at := now();
        NEW.last_error := left(coalesce(NEW.last_error, '') ||
            ' [dead: the retry limit (8) reached — the terminal poison class]', 512);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SET search_path = pg_catalog, arv;
DROP TRIGGER IF EXISTS job_poison_guard ON arv.job;
CREATE TRIGGER job_poison_guard BEFORE INSERT OR UPDATE ON arv.job
    FOR EACH ROW EXECUTE FUNCTION arv.job_poison_guard();

GRANT SELECT, INSERT, UPDATE ON arv.job TO arv_app;
GRANT SELECT ON arv.job TO arv_read;
REVOKE EXECUTE ON FUNCTION arv.job_claim(TEXT, INTEGER, INTEGER) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION arv.job_claim(TEXT, INTEGER, INTEGER) TO arv_app;
REVOKE EXECUTE ON FUNCTION arv.job_complete(UUID, TEXT, BIGINT, TEXT, TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION arv.job_complete(UUID, TEXT, BIGINT, TEXT, TEXT) TO arv_app;
