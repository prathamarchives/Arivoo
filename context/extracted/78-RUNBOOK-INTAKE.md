# 78 — THE RUNBOOK-EXECUTION INTAKE (CLAIM-087)

> STATUS: SESSION ENGINEERING RECORD — ACTIVE (session 53, 2026-11-18; owner turn 45; D-022: historical process artifact, NOT owner intent). PR this session: #126 (CLAIM-087, disposition: open → merged under INT-145's single-actor path).

## §1 — the turn, verbatim

The owner's chat turn (2026-11-18):

> "maybe js install the cli and i give you the acess token"

> "sbp_[REDACTED — D-025: the access token never enters preserved material; it lives only in the sandbox's .secrets store] here is the token acesss and setup supabase cli and then start executing step by step non stop until done from the doc attached"

Attached: the runbook, "Arivo Full-Stack Backend Execution Runbook" v1.0, 1075 lines — verbatim at `context/raw/ARIVO_FULL_STACK_BACKEND_EXECUTION_RUNBOOK.md` (SHA-256 `2113dcfb…`, the §9 growth register's THIRD use; register + §1 coverage + §2 turn row + full-digest block all landed; the §2 turn-43/44 rows were found missing from the provenance registry and repaired in this slice — the drift note below).

## §2 — what the turn establishes (the directive, distilled — never reworded as owner words)

The owner supplies the connection (the scoped Supabase PAT), orders the CLI setup, and orders non-stop step-by-step execution of the attached runbook. The runbook is the execution authority for the productionization chain INT-151 reserved: 13 phases, 8 waves, the §21 prohibited-shortcuts list, the §23 final production definition. Its §0 carries the honest-stop rule (gated actions stop, get named, work continues). Its own §3.1 embeds this repository's slice protocol (AGENTS/STATE/CLAIMS → branch → RED → implement → verify → SEV → PR → merge) — the runbook and the repository's law are one workflow, not two.

## §3 — Phase 0+1 executed before the intake (the session's pre-slice)

- The PAT is scoped exactly as §5.2 wants: **exactly one project visible — `arivo` (`wcuuakhdmsmmxagvbdmg`, ap-south-1, ACTIVE_HEALTHY)**. No account-wide visibility.
- Supabase CLI **v3.2.0** installed (the official binary; the v2.30.17 tag 404'd — v3 is current). Project linked. `login`'s flag form changed in v3; the env-var form (`SUPABASE_ACCESS_TOKEN`) is the working path.
- Live state verified = §1.3 EXACTLY: no `arv` schema (schemas: auth/extensions/graphql/graphql_public/pgbouncer/public/realtime/storage/vault only), 0 app tables, no `arv_app`/`arv_read` roles (only the supabase defaults: postgres/authenticated/anon/service_role), 0 buckets, 0 edge functions, extensions = pg_stat_statements/pgcrypto/plpgsql/supabase_vault/uuid-ossp (`vector` ABSENT — not merely uninstalled-and-available), postgres DB 11 MB empty, advisors security `{'lints': []}`.
- **The read-only SQL path works**: POST `/v1/projects/{ref}/database/query` with the PAT executes as `supabase_admin`-class authority — this is the migration-stage channel §5.2's "add Database write" step anticipates. A second admin path (`supabase inspect db --remote`) also verified working through the linked project.

## §4 — the honest ledger mechanics this slice executed

- INT-152 (the turn: token + setup + non-stop; the token REDACTED from preservation, per D-025) + INT-153 (the runbook-execution chain reservation). Numbering note extended (INT-152..153); ledger count 133 → 135; AGENTS/STATE mirrors follow.
- **The CLAIMS registry-drift's THIRD instance (the 086 close row) + the §2 provenance-registry drift (the manifest's turn-43/44 rows) — both repaired in this slice:** the #125 merge's rebase-era restructure left 086's OPEN row without its closed row (the class's third instance — record 77 §4's escalation line is now live: the next step is the named mutation case, and this session records that the escalation is due); the manifest's turn-table itself was missing turn-43/44 rows. Both repaired with the merge facts; the honest note is that the class now spans both files (CLAIMS + the manifest).
- **The §2 provenance-registry drift repaired**: the manifest's turn-table was missing turn-43 and turn-44 rows entirely (both prior documents' register/§1 rows were present, but the chat-turn provenance rows never landed). This slice adds turn-43/44/45 in order. The drift class is noted in record 77 §4's escalation line — this instance is the manifest-table variant of it.
- D-047 lands the runbook adoption (the execution authority; the wave order; the stop conditions).

## §5 — the execution now underway (D-047's waves; the §22 executor report at each boundary)

Wave A (readiness): this intake slice + the §4.4 preflight + the provider-access status. Wave B (the Supabase DB foundation): CLAIM-088 the guarded remote-target migration path (the loopback guard preserved; explicit remote mode; RED-first tests; the local chain green first), then CLAIM-089 the remote application (the least-privilege roles; migrations 0001→0019; the RLS/ledger verification evidence). Wave C is Q12-gated (storage provider decision), Wave F is cost-gated (Railway account/cost approval), Wave G needs the real desktop repository (not yet identified — the runbook §4.3's own rule: do not guess the repo name).

## §6 — the runbook's provider recommendations vs the repository's open decisions (kept distinct)

The runbook recommends Railway/Singapore (Wave F's host) and a private Supabase Storage bucket (Wave C's provider) — **recommendations, not ratified decisions**: Q17 (storage provider + cross-store recovery) and Q18 (deployment host) remain the open homes; the runbook's own §0 (and Q12's rule) forbids silently closing them. The runs record each gate honestly at its wave boundary.
