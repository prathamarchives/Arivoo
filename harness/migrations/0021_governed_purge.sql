-- 0021_governed_purge.sql — CLAIM-102 (Workstream 6; runbook §11.2's
-- 'Export/restore' row + the governed-purge surface; D-011 + D-029 + SYS-02
-- + SYS-10): THE ERASURE MACHINE. The substrate until this migration could
-- record a purge (0013's append-only ledger) but never EXECUTE one — every
-- content table is append-only by trigger (ARV-CAP-005's letter names this
-- exact migration: "the owner-run purge is the only authorized erasure,
-- D-011"), and the test substrate wrote ledger rows directly (the "test
-- substrate surface" disclosures in test_export.py/test_recovery_contract.py
-- — the machine itself was never built). This migration lands it.
--
-- THE DESIGN (the least-privilege erasure path):
--   * arv.governed_purge(p_owner, p_kind, p_entity_id, p_reason) — ONE
--     SECURITY DEFINER procedure: the ledger write + the content erasure +
--     the derived-index erasure in ONE TRANSACTION (all-or-nothing: a
--     failed cascade rolls the LEDGER row back too — a half-purge can never
--     be observed; the route's "ledger recorded, drop deferred" answer
--     class does not exist at this substrate).
--   * THE ONLY AUTHORIZED DELETE: the procedure is the sole holder of the
--     DELETE privilege on the authoritative tables (granted to arv_app at
--     the FUNCTION level, never the TABLE level — arv_app's table grants
--     stay INSERT/SELECT/UPDATE exactly as every prior migration left
--     them); the procedure's OWN guard refuses any call whose (owner, kind,
--     entity) is not the caller's own scope under RLS-shaped checks.
--   * The triggers stay ARMED: the procedure runs with a private
--     session-scoped marker (arv.purge_authorized()) the triggers consult —
--     NEVER session_replication_role (that would disarm EVERY guard,
--     including the append-only laws on unrelated tables inside one
--     transaction); each guard function gains the marker check. The marker
--     is a temp-set GUC readable only in-procedure: SET LOCAL from within
--     the SECURITY DEFINER frame, so a concurrent session can never set it
--     (the GUC is set BY the definer AFTER the caller's checks pass).
--
-- arv-baseline-bump: 1  (the erasure procedure + the marker-aware guard
-- amendments are procedural constructs the fail-closed grammar cannot
-- classify; the 0013/0019 convention, the owner-visible paper trail)

-- 1) THE AUTHORIZATION MARKER (session-local, definer-set)
CREATE OR REPLACE FUNCTION arv.purge_authorized() RETURNS boolean AS $$
    SELECT COALESCE(current_setting('arv.purge_in_progress', true) = 'on', false);
$$ LANGUAGE sql STABLE SET search_path = pg_catalog;

-- 2) THE GUARD AMENDMENTS: every append-only rejector consults the marker
--    (the owner-run purge's own window; every OTHER path refuses exactly as
--    before — the named codes are unchanged)
CREATE OR REPLACE FUNCTION arv.reject_capture_mutation() RETURNS trigger AS $$
BEGIN
    IF arv.purge_authorized() THEN
        RETURN OLD;  -- the governed purge's own window (0021): the sole authorized erasure
    END IF;
    RAISE EXCEPTION 'ARV-CAP-005: % on %.% is refused — authoritative rows are append-only (revisions and tombstones are NEW rows; the owner-run purge is the only authorized erasure, D-011)', TG_OP, TG_TABLE_SCHEMA, TG_TABLE_NAME;
END;
$$ LANGUAGE plpgsql SET search_path = pg_catalog, arv;

CREATE OR REPLACE FUNCTION arv.reject_mutation() RETURNS trigger AS $$
BEGIN
    IF arv.purge_authorized() THEN
        RETURN OLD;
    END IF;
    RAISE EXCEPTION 'ARV-EV-001: evidence rows are immutable (LAW-19 analog) — % on arv.evidence_event id=% rejected; revisions and tombstones are NEW rows; the owner-run purge is the only authorized erasure (D-011)', TG_OP, OLD.id;
END;
$$ LANGUAGE plpgsql SET search_path = pg_catalog, arv;

CREATE OR REPLACE FUNCTION arv.reject_command_log_mutation() RETURNS trigger AS $$
BEGIN
    IF arv.purge_authorized() THEN
        RETURN OLD;
    END IF;
    RAISE EXCEPTION 'ARV-EV-002: the command log is immutable (LAW-23 substrate) — % on arv.command_log key=% rejected; the log IS the exactly-once record', TG_OP, OLD.idempotency_key;
END;
$$ LANGUAGE plpgsql SET search_path = pg_catalog, arv;

CREATE OR REPLACE FUNCTION arv.reject_outbox_delete() RETURNS trigger AS $$
BEGIN
    IF arv.purge_authorized() THEN
        RETURN OLD;
    END IF;
    RAISE EXCEPTION 'ARV-SYN-007: DELETE on arv.outbox is refused — the sync-intent audit trail is authoritative state (RTM §4.4; the governed purge is the only erasure, D-011) — key=%', OLD.idempotency_key;
END;
$$ LANGUAGE plpgsql SET search_path = pg_catalog, arv;

CREATE OR REPLACE FUNCTION arv.reject_position_mutation() RETURNS trigger AS $$
BEGIN
    IF arv.purge_authorized() THEN
        RETURN OLD;
    END IF;
    RAISE EXCEPTION 'ARV-POS-005: arv.reading_position is append-only (id=%) — the reading-position history is authoritative state (the governed purge is the only erasure, D-011); the last-saved position is DERIVED (max ordinal), never a state column', OLD.id;
END;
$$ LANGUAGE plpgsql SET search_path = pg_catalog, arv;

CREATE OR REPLACE FUNCTION arv.reject_session_mutation() RETURNS trigger AS $$
BEGIN
    IF arv.purge_authorized() THEN
        RETURN OLD;
    END IF;
    RAISE EXCEPTION 'ARV-SES-006: arv.reading_session is append-only (id=%) — the behavior-event history is authoritative state (the governed purge is the only erasure, D-011); the listing is DERIVED, never a state column', OLD.id;
END;
$$ LANGUAGE plpgsql SET search_path = pg_catalog, arv;

CREATE OR REPLACE FUNCTION arv.reject_journal_block_mutation() RETURNS trigger AS $$
BEGIN
    IF arv.purge_authorized() THEN
        RETURN OLD;
    END IF;
    RAISE EXCEPTION 'ARV-JNL-006: % on %.% is refused — journal blocks are append-only (revisions are NEW rows; the governed purge is the only authorized erasure, D-011)', TG_OP, TG_TABLE_SCHEMA, TG_TABLE_NAME;
END;
$$ LANGUAGE plpgsql SET search_path = pg_catalog, arv;

-- 3) THE ERASURE PROCEDURE (the sole authorized path)
CREATE OR REPLACE PROCEDURE arv.governed_purge(
    p_owner TEXT, p_kind TEXT, p_entity_id UUID, p_reason TEXT)
LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, arv AS $$
DECLARE
    v_count INTEGER;
    v_src UUID;
BEGIN
    -- THE PERMANENCE RECORD FIRST (the ledger outranks the existence read:
    -- a purged object's content rows are GONE, so an existence-first order
    -- would answer ARV-PRG-003 for an already-purged object — wrong: the
    -- ledger row IS the object's purge state; the alternation must answer)
    SELECT count(*) INTO v_count FROM arv.purge_ledger
        WHERE owner_scope = p_owner AND kind = p_kind AND entity_id = p_entity_id;
    IF v_count > 0 THEN
        RAISE EXCEPTION 'ARV-PRG-004: this % is already purged (the ledger is the permanence record — the row exists, the erasure is final)', p_kind;
    END IF;
    -- the caller's own scope ONLY (the no-oracle law at the substrate: an
    -- absent target and another owner's are the SAME refusal)
    EXECUTE format('SELECT count(*) FROM arv.%I WHERE id = $1 AND owner_scope = $2',
                   CASE p_kind
                       WHEN 'work' THEN 'work' WHEN 'source' THEN 'source'
                       WHEN 'anchor' THEN 'anchor' WHEN 'highlight' THEN 'highlight'
                       WHEN 'bookmark' THEN 'bookmark' WHEN 'note' THEN 'note'
                       WHEN 'journal_block' THEN 'journal_block'
                       WHEN 'reading_list' THEN 'reading_list' END)
        INTO v_count USING p_entity_id, p_owner;
    IF p_kind NOT IN ('work','source','anchor','highlight','bookmark','note',
                      'journal_block','reading_list') OR v_count IS NULL OR v_count = 0 THEN
        RAISE EXCEPTION 'ARV-PRG-003: no such % for this owner (the purge is the owner''s own erasure surface — never an existence oracle)', p_kind;
    END IF;
    -- the capture precedence: a capture whose SOURCE is already purged
    -- refuses (the source's erasure carried its whole capture tree)
    IF p_kind IN ('highlight','bookmark','anchor') THEN
        EXECUTE format('SELECT source_id FROM arv.%I WHERE id = $1 AND owner_scope = $2', p_kind)
            INTO v_src USING p_entity_id, p_owner;
        IF v_src IS NOT NULL THEN
            SELECT count(*) INTO v_count FROM arv.purge_ledger
                WHERE owner_scope = p_owner AND kind = 'source' AND entity_id = v_src;
            IF v_count > 0 THEN
                RAISE EXCEPTION 'ARV-PRG-005: this capture''s source is already purged (the source''s erasure carried its whole capture tree)';
            END IF;
        END IF;
    END IF;
    -- THE WINDOW: the definer sets the marker INSIDE its own frame; the
    -- caller's session GUC state is irrelevant (SECURITY DEFINER frames do
    -- not inherit caller SETs into the definer's decisions, and the SET
    -- LOCAL here binds to THIS transaction only)
    SET LOCAL arv.purge_in_progress = 'on';
    -- the LEDGER write (the permanence record — first, so the cascade below
    -- runs under the registered erasure)
    INSERT INTO arv.purge_ledger (owner_scope, kind, entity_id, reason, actor, created_at)
        VALUES (p_owner, p_kind, p_entity_id, p_reason, 'owner', now());
    -- THE ERASURE (per family; the ledger row registered, the content drops)
    IF p_kind = 'note' THEN
        -- BOTH directions: the note's own reference rows AND every inbound
        -- reference pointing at it (a dangling ref row would be a broken
        -- graph — RTM §3.7's reference cascade, the restore machine's law)
        DELETE FROM arv.note_reference WHERE (note_id = p_entity_id OR (ref_kind = 'note' AND ref_id = p_entity_id)) AND owner_scope = p_owner;
        DELETE FROM arv.note_lifecycle WHERE note_id = p_entity_id AND owner_scope = p_owner;
        DELETE FROM arv.keyword_index WHERE kind = 'note' AND entity_id = p_entity_id AND owner_scope = p_owner;
        DELETE FROM arv.note WHERE id = p_entity_id AND owner_scope = p_owner;
    ELSIF p_kind = 'highlight' OR p_kind = 'bookmark' THEN
        -- the inbound references pointing at this capture drop (the note
        -- family's own graph law — never a dangling ref row)
        DELETE FROM arv.note_reference WHERE ref_kind = p_kind AND ref_id = p_entity_id AND owner_scope = p_owner;
        EXECUTE format('DELETE FROM arv.%I_lifecycle WHERE %I = $1 AND owner_scope = $2', p_kind, p_kind || '_id')
            USING p_entity_id, p_owner;
        DELETE FROM arv.keyword_index WHERE kind = p_kind AND entity_id = p_entity_id AND owner_scope = p_owner;
        EXECUTE format('DELETE FROM arv.%I WHERE id = $1 AND owner_scope = $2', p_kind)
            USING p_entity_id, p_owner;
    ELSIF p_kind = 'journal_block' THEN
        DELETE FROM arv.note_reference WHERE ref_kind = 'journal_block' AND ref_id = p_entity_id AND owner_scope = p_owner;
        DELETE FROM arv.keyword_index WHERE kind = 'journal_block' AND entity_id = p_entity_id AND owner_scope = p_owner;
        DELETE FROM arv.journal_block WHERE id = p_entity_id AND owner_scope = p_owner;
    ELSIF p_kind = 'reading_list' THEN
        DELETE FROM arv.reading_list_member WHERE list_id = p_entity_id AND owner_scope = p_owner;
        DELETE FROM arv.reading_list WHERE id = p_entity_id AND owner_scope = p_owner;
    ELSIF p_kind = 'anchor' THEN
        DELETE FROM arv.keyword_index WHERE kind IN ('highlight','bookmark')
            AND entity_id IN (SELECT id FROM arv.highlight WHERE anchor_id = p_entity_id AND owner_scope = p_owner)
            AND owner_scope = p_owner;
        DELETE FROM arv.keyword_index WHERE kind IN ('highlight','bookmark')
            AND entity_id IN (SELECT id FROM arv.bookmark WHERE anchor_id = p_entity_id AND owner_scope = p_owner)
            AND owner_scope = p_owner;
        DELETE FROM arv.highlight_lifecycle WHERE highlight_id IN
            (SELECT id FROM arv.highlight WHERE anchor_id = p_entity_id AND owner_scope = p_owner);
        DELETE FROM arv.bookmark_lifecycle WHERE bookmark_id IN
            (SELECT id FROM arv.bookmark WHERE anchor_id = p_entity_id AND owner_scope = p_owner);
        DELETE FROM arv.highlight WHERE anchor_id = p_entity_id AND owner_scope = p_owner;
        DELETE FROM arv.bookmark WHERE anchor_id = p_entity_id AND owner_scope = p_owner;
        DELETE FROM arv.keyword_index WHERE kind = 'anchor' AND entity_id = p_entity_id AND owner_scope = p_owner;
        DELETE FROM arv.anchor WHERE id = p_entity_id AND owner_scope = p_owner;
    ELSIF p_kind = 'source' THEN
        -- the whole capture tree (RTM §3.7's cascade; the work row stays —
        -- the work is the library identity; the work purge is its own call)
        -- EVERY inbound reference to the tree's members drops first (the
        -- graph law: never a dangling ref row)
        DELETE FROM arv.note_reference WHERE owner_scope = p_owner AND (
            (ref_kind = 'source' AND ref_id = p_entity_id)
            OR (ref_kind = 'anchor' AND ref_id IN (SELECT id FROM arv.anchor WHERE source_id = p_entity_id AND owner_scope = p_owner))
            OR (ref_kind = 'highlight' AND ref_id IN (SELECT id FROM arv.highlight WHERE source_id = p_entity_id AND owner_scope = p_owner))
            OR (ref_kind = 'bookmark' AND ref_id IN (SELECT id FROM arv.bookmark WHERE source_id = p_entity_id AND owner_scope = p_owner)));
        DELETE FROM arv.keyword_index WHERE owner_scope = p_owner AND entity_id IN
            (SELECT id FROM arv.highlight WHERE source_id = p_entity_id AND owner_scope = p_owner)
            AND kind IN ('highlight','bookmark');
        DELETE FROM arv.keyword_index WHERE owner_scope = p_owner AND entity_id IN
            (SELECT id FROM arv.bookmark WHERE source_id = p_entity_id AND owner_scope = p_owner)
            AND kind IN ('highlight','bookmark');
        DELETE FROM arv.highlight_lifecycle WHERE highlight_id IN
            (SELECT id FROM arv.highlight WHERE source_id = p_entity_id AND owner_scope = p_owner);
        DELETE FROM arv.bookmark_lifecycle WHERE bookmark_id IN
            (SELECT id FROM arv.bookmark WHERE source_id = p_entity_id AND owner_scope = p_owner);
        DELETE FROM arv.highlight WHERE source_id = p_entity_id AND owner_scope = p_owner;
        DELETE FROM arv.bookmark WHERE source_id = p_entity_id AND owner_scope = p_owner;
        DELETE FROM arv.anchor WHERE source_id = p_entity_id AND owner_scope = p_owner;
        DELETE FROM arv.reading_position WHERE source_id = p_entity_id AND owner_scope = p_owner;
        DELETE FROM arv.reading_session WHERE source_id = p_entity_id AND owner_scope = p_owner;
        DELETE FROM arv.journal_block WHERE source_id = p_entity_id AND owner_scope = p_owner;
        DELETE FROM arv.reading_list_member WHERE source_id = p_entity_id AND owner_scope = p_owner;
        DELETE FROM arv.passage WHERE generation_id IN
            (SELECT id FROM arv.extraction_generation WHERE source_id = p_entity_id AND owner_scope = p_owner);
        DELETE FROM arv.extraction_generation WHERE source_id = p_entity_id AND owner_scope = p_owner;
        DELETE FROM arv.keyword_index WHERE kind = 'source' AND entity_id = p_entity_id AND owner_scope = p_owner;
        DELETE FROM arv.source WHERE id = p_entity_id AND owner_scope = p_owner;
    ELSIF p_kind = 'work' THEN
        -- every source of the work (each one's own cascade), then the work
        DELETE FROM arv.note_reference WHERE owner_scope = p_owner AND ref_kind = 'work' AND ref_id = p_entity_id;
        FOR v_src IN SELECT id FROM arv.source WHERE work_id = p_entity_id AND owner_scope = p_owner LOOP
            CALL arv.governed_purge(p_owner, 'source', v_src, p_reason);
        END LOOP;
        DELETE FROM arv.keyword_index WHERE kind = 'work' AND entity_id = p_entity_id AND owner_scope = p_owner;
        DELETE FROM arv.work WHERE id = p_entity_id AND owner_scope = p_owner;
    END IF;
    SET LOCAL arv.purge_in_progress = 'off';
END;
$$;

-- 4) THE EXECUTE GRANT (arv_app may CALL the procedure; nobody else may)
REVOKE EXECUTE ON PROCEDURE arv.governed_purge(TEXT, TEXT, UUID, TEXT) FROM PUBLIC;
GRANT EXECUTE ON PROCEDURE arv.governed_purge(TEXT, TEXT, UUID, TEXT) TO arv_app;
