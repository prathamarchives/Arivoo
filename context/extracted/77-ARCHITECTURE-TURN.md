# 77 — THE ARCHITECTURE-CHANGE TURN (CLAIM-086)

> STATUS: SESSION ENGINEERING RECORD — ACTIVE (session 52, 2026-11-18; owner turn 44; D-022: historical process artifact, NOT owner intent). PR this session: #125 (CLAIM-086, disposition: open → merged under INT-145's single-actor path).

## §1 — the turn, verbatim

The owner's chat turn (2026-11-18):

> "theres a change in artithecuree... skipping kev."

Attached: a 482-line document, "Arivo backend status and completion report" (Repository and Supabase audit · 18 November 2026) — verbatim at `context/raw/ARIVO_BACKEND_STATUS_REPORT.txt`, SHA-256 `a344ec6235557531ceab5e0117a35b93f70f0442f735d26da7c4d10e6fe4df1d`, admitted through the §9 growth register (the register's SECOND use — the first was the Kev spec itself; no verifier edit needed, exactly the transition form's design).

## §2 — what the turn changes (the directive, distilled — never reworded as owner words)

**Kev is skipped.** The two-repository architecture (INT-148's execution half + INT-149's chain) is superseded by INT-150. The kev repository (BOOT-001, `prathamarchives/kev`) is PARKED: preserved as-is, never deleted (nothing in the turn asks for deletion; the repo is private and inert). No further Kev work.

**Arivo becomes the standalone production product.** The report's own final position: "extend the existing backend into this architecture, not start another backend from scratch." The target architecture (report §5): the desktop client → Supabase Auth → the Arivo backend API (the existing command kernel + query layer) → Supabase PostgreSQL (canonical state) + private object storage + background workers. The main rule: the desktop client never gets privileged database access.

**The report's own assessment of what exists** (§2, verified against this repo): the command kernel (`harness/commands.py` — transactional, idempotent, provenance-carrying), the migration chain through `0019_agent_access.sql`, the import/extraction pipeline, the reading/capture/journal surfaces, the two-outbox sync design, keyword retrieval + context packs (5A/5B complete), the read-only MCP server (22 tools, stdio). What does NOT exist: the production HTTP API, Supabase Auth integration, the remote database adapter (`harness/adapters/pg.py` is loopback-only by ARV-DB-004 — intentional for the test rig), cloud file storage, hosted workers, deployment. The Supabase project `arivo` (Mumbai, ap-south-1) is ACTIVE_HEALTHY but EMPTY (0 migrations, 0 tables, 0 roles, 0 buckets, 0 functions; `vector` available-not-installed).

## §3 — the adopted execution order (D-046; the report's §9, its own words' structure)

1. **Architecture and repository reconciliation** (THIS slice: the intake + the navigation repair — the report's workstream 1, executed first exactly as the report directs: "The executor should first reconcile these references, update the current-state snapshot, and ensure the implementation plan contains only Arivo's actual product requirements").
2. Production database adapter + the Supabase schema (a SEPARATE production adapter; the local rig adapter stays for tests; the owner-from-token rule replaces client-supplied owner; migrations reviewed for Supabase compatibility before application).
3. Object storage + import recovery (the staged/hash/upload/verify/finalize contract; a provider decision recorded before provider-specific schema).
4. The HTTP API + Supabase Auth (the versioned endpoints over the existing command/query kernel — the adapter translates, never re-creates business rules; two-user isolation proven).
5. The worker system (a dedicated durable job machine — separate from both outboxes, per the report's explicit warning).
6. Desktop persistence + sync (the real client; the local-store decision made explicitly, never a casual SQLite swap).
7. Deployment + system validation (the completion gate: a real user's full workflow surviving restart/offline/restore/purge).
8. Advanced retrieval (5C–5G under their existing gates; `vector` enabled only with the approved semantic-index work).

## §4 — the honest ledger mechanics this slice executed

- INT-150 (the turn, verbatim + grounds: the Kev chain superseded; the kev repo parked) + INT-151 (the productionization chain reservation — so the next session enters with the scope claimed).
- The numbering note extended (INT-150..151); the ledger count 131 → 133; AGENTS/STATE counts follow (one fact, one home: the count lives in the ledger, the mirrors cite it).
- **The CLAIMS registry-drift repair (the second instance of the class):** the #124 merge's rebase-era restructure landed CLAIM-084b's OPEN row without its closed row (the same class as #121's slice-A restructure — the rebase dropped the close-row edit, and the idempotent rebuild guard saw the open row and skipped). This slice retires the stale open row and adds the closed row with the merge facts. The class now has two instances; if a third appears, the repair belongs in the claims registry's own guard (a named mutation case), not another hand repair.
- **Q13/Q14/Q15 retired with outcome** (each: superseded, basis INT-150 — the questions asked about the Kev architecture the owner just skipped; their SUBSTANCE re-registered where it still bites: Q14's never-delete-the-inactive-projects constraint carries into the productionization era as a standing safety note in D-046's basis).
- **Q17/Q18/Q19 registered** (the report's own still-open decisions, restated at Arivo scope): Q17 the storage provider + cross-store recovery contract (the report: "the provider and cross-store recovery contract are not yet finalized... must be recorded before provider-specific schema"); Q18 the deployment host (the report: "I would not assume Vercel is the right host... select it only if its runtime model fits"); Q19 the desktop local-store contract (the report: "how the desktop stores its local working data... needs its own implementation and contract").
- Q16 unchanged (the growth-register authority — now exercised twice, both clean); Q6–Q12, D-014 unchanged.

## §5 — the navigation reconciliation (workstream 1's deliverables)

STATE's five areas rewritten (phase: THE PRODUCTIONIZATION ERA; active: CLAIM-086; next: D-046 workstream 2 — the production adapter slice). AGENTS' phase line + purpose rewritten (the standalone product boundary; the Kev intake lines superseded). PLAN's Kev rows (5H's gate, Q13–Q15) re-pointed: 5H becomes the retrieval-evaluation gate inside Arivo (its policy/evaluation substance preserved — the report keeps 5C–5G behind their gates); 5C–5G stay as the advanced-retrieval roadmap (report §7's own table). EXECUTION's §6 Q-mirror updated (Q13–Q15 out, Q17–Q19 in). The 5F/5H meeting point recorded: 5F grounded-relationship promotion needs 5H's evaluation gate passed INSIDE Arivo now (the Kev-side gate is gone with the architecture).

## §6 — what workstream 2 looks like (the next slice, claimed by INT-151)

`harness/adapters/pg_prod.py` (or the agreed name): the production connection path — the loopback-only boundary STAYS in the test adapter (its ARV-DB-004 refusal is a feature); the production adapter carries its own explicit, reviewed connection surface (pooling, timeouts, transaction management; no subprocess psql for the long-running service). Plus the migration-chain review for Supabase compatibility. The slice lands RED-first against a simulated remote before any real Supabase write (the project's emptiness is verified fact; Q14's provisioning confirmation requirement now lives in D-046's basis, not a blocking question).
