-- 0020_search_path_pins.sql — the SECURITY DEFINER search_path pins
-- (CLAIM-093; INT-158/D-051; the runbook §7.4's hardening step; the CLAIM-089
-- advisors' P2 debt).
--
-- THE OBSERVED STATE (this slice's live probe, both the local rig AND the
-- remote project — identical, the ledger equivalence holding):
--   * arv.agent_token_lookup is the ONLY SECURITY DEFINER function in arv —
--     and it is ALREADY pinned (search_path = pg_catalog, arv; migration 0019)
--   * the other 23 arv functions are plain (non-SECURITY-DEFINER) guards/
--     rejectors: they run at the CALLER's search_path — exactly the intended
--     behavior for trigger guards on owner-scoped tables
--   * the advisors' 23 WARNs named Supabase's own platform schemas
--     (storage/auth) — platform-managed, already pinned by Supabase itself,
--     outside the owner's migration chain (touching them would violate the
--     one-history rule)
--
-- THIS MIGRATION is a HARD GUARANTEE, not a repair:
--   1) ALTER FUNCTION pins the definer function explicitly (a no-op today —
--      belt)
--   2) ALTER ROLE ... IN DATABASE sets the runtime role's default search_path
--      (pg_catalog first, arv second): the API's arv_app sessions resolve
--      catalog objects FIRST — a hostile object shadowing pg_catalog names
--      can never be picked up (the search-path hijack class, closed by
--      default rather than by convention)
--   3) the verification half lives in the test suite: the invariant (ZERO
--      unpinned SECURITY DEFINER functions in arv) is CHECKED on every
--      future migration run — the state was conformant; now it cannot
--      regress silently

-- 1) the belt: pin the definer function explicitly (no-op on today's shape)
ALTER FUNCTION arv.agent_token_lookup(text) SET search_path = pg_catalog, arv;

-- 2) the runtime roles' GLOBAL default resolution order (pg_catalog FIRST —
--    the hijack-proof order; 'public' second, the standard shape). 'arv' stays
--    OFF the roles' default path: the kernel's own SQL qualifies arv.X
--    explicitly everywhere (grep-verified: commands.py/query.py carry no
--    unqualified arv object references), and keeping 'arv' off the path keeps
--    pg_get_constraintdef's rendering stable for every role (the JNL-06 class:
--    an on-path schema changes how constraint defs render, breaking
--    string-shaped audits). The role-level default (not IN DATABASE ...):
--    it holds on EVERY database the role touches — the remote's postgres, the
--    local rig's scratch dbs, and any future physical replica alike.
ALTER ROLE arv_app SET search_path = pg_catalog, public;
ALTER ROLE arv_read SET search_path = pg_catalog, public;
