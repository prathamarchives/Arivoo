# 18 — RESEARCH-DRIVEN REVIEW AND PHASE-2 FOUNDATION EXECUTION

> STATUS: SESSION ENGINEERING RECORD (2026-10-16; owner turns 15–16; INT-120/INT-121; D-036). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 17. PRs this session: #27 (review intake + drift repair) · #28–#31 (Phase 2 Layer 2.1, slices S1–S4) · #32 (session close) · #33 (harness probe, closed unmerged). §1–§3 land at intake; §4+ grow per slice and are completed at session close.

## 1. What the owner asked (verbatim — owner turns 15 and 16, 2026-10-16)

### Owner turn 15 (the eight-part review directive — preservation boundary stated)

The turn directed a research-driven architecture review of the repository: eight review parts under four roles (principal systems architect + research workflow designer + backend engineer + independent verification engineer), producing a nine-section review report and a Phase 1/2 foundation plan, with the attached research-methods video transcript as the designated product north star and a second, different transcript by the same creator (the "original thinking" video) pasted inline and treated as a corroborating source. The governing quality bar was **"deeper, not bigger"** — no needless layers, frameworks, or abstractions, but "minimum" never treated as a ceiling: cheap-to-build/retro-expensive foundations are built early. The turn required four pre-alignment answers before execution ((1) what top professionals would do that was not asked; (2) what most raw source material they would start from; (3) what specific methods and tools they would use; (4) what besides the participants could prove the results correct) — answered in the review's method sections before execution began. The session was constrained to read-only forensics with a live uncoached fresh-context agent exam as independent evidence.

**Preservation boundary (stated honestly, LAW-04):** the turn's full verbatim text crossed a host context boundary before this session, and the no-mutation constraint was honored at the time — nothing was preserved in-repo during the review session. The fragments below are the verbatim fragments carried across by the host session-continuation summary (the E-2 cross-check class for INT-120); the review artifact `context/reviews/2026-10-16-research-driven-architecture-review.md` is the durable record of the directive's operational content and of everything done under it. Quote fidelity outranks completeness: a fabricated "verbatim" turn would be the worse failure (VER-803's spirit).

> "现在是执行轮——对着仓库跑起来，并保留这一切：所有迭代、新北极星、本应已完成的一切；保持默认的日志、上下文与记忆提取；我之前说的是不要执行代码（改仓库）"
> ("This is the execution round — run it against the repository, and keep all of it: every iteration, the new north star, everything that should already be done; keep the default logging, context, and memory extraction; what I said before was: do not execute code (modify the repository).")

> "更深而非更大"
> ("Deeper, not bigger" — the review's governing quality bar, applied throughout: no unnecessary machinery, but foundations that are cheap now and retro-expensive later are not deferred.)

### Owner turn 16 (verbatim — the execution directive this session executes)

> "read, push, understand, gather all the context and execute phase 2 foundation. but before that update the repo on everything we did rightnow in last convos"

(The turn re-supplied the review deliverable as an upload — `arivoo-review-2026-10-16.md` — now preserved verbatim at `context/reviews/2026-10-16-research-driven-architecture-review.md`.) The turn, read per the authority order (EXECUTION §3, EXR-08 — the latest owner statement governs): (a) the turn-15 no-mutation constraint is lifted for this session's work; (b) everything done in the prior conversation lands in the repo (the review artifact + its findings + this session's intake and ledger entries); (c) Phase 2 foundation — the review's §7 slices — is executed; (d) "push" = land the work through the repo's gates (branch + PR + CI + merge, D-024/P-15).

## 2. Starting state

- Local HEAD `224e5b8f6a413fe54accbe439af8fe0b5dffb000` = remote `origin/main` (no ahead/behind); working tree clean before any edit; `git fsck` clean (re-verified last session, review §1.1).
- Preflight runs this session (all BEFORE any edit, at `224e5b8`):
  - `python3 tools/verify_canonical_layer.py` → exit 0 → **51/0** (51 unique VER-IDs, 0 failures)
  - `python3 tools/verify_selftest.py` → exit 0 → **30/30** known-bad mutations caught
  - `python3 tools/isolation_check.py` → exit 0 → **GREEN** (conditions printed, values never)
  - `python3 tools/isolation_selftest.py` → exit 0 → **18/18** matrix cases
- Remote state (GitHub API probe, token from the out-of-repo store, never printed): main = `224e5b8` (identical to local); protection PRESENT — required = `[canonical-layer, head-tools]`, strict, admins included, no force push, no deletions; **0 open PRs**; CI on main green — run `38686615817` (push, `224e5b8`, both jobs success; PR #26's post-merge run — the standing close-gap, already observed last session and re-confirmed now); repo visibility observed `private=False` (public — registered as Q9, owner-gated).
- Phase 1 GRADUATED and standing (graduation evidence: record 17 §4.3/§7; corroborated independently by the review session's re-runs and cold-start exam, review §1.1).
- Environment note (this session's build context, not a repo fact): the host sandbox has no preinstalled Postgres; a user-space PostgreSQL 17.11 cluster (Debian packages, extracted without privileges, out-of-repo at `/home/z/my-project/.pg/`) serves as the local real stack for preflight; CI uses a `postgres:17` service container — the version-parity FACT lands with S1 (F-001).

## 3. Task and scope

- **Requested work:** (1) update the repository on everything done in the prior conversation (the 2026-10-16 research-driven architecture review: artifact + intake + the review's drift findings F-1..F-8 repaired); (2) execute the Phase 2 foundation — the review's §7 slices S1–S4 (Layer 2.1, the minimum trustworthy harness, P-17-scoped), Rider A folded (substrate conventions + migrations machinery explicit).
- **Intent/decision references:** INT-121 (the execution directive) · INT-120 (the review directive, preserved fragments) · D-036 (the adoption) · D-024 (change channel: the review artifact merges under the owner's explicit authorization given this turn) · P-13/P-15 (standing authorization for memory deltas and slices) · D-025/D-035 (the wall-construction-with-evidence pattern the S1 CI job follows).
- **Bounded scope:** intake PR (review artifact + record 18 §1–§3 + ledger + decisions + register + drift repair F-1..F-5, F-8) → S1 (rig + migrations v0 + CI Postgres job + FACT) → S2 (substrate-convention table: immutability triggers, RLS, roles, tombstone, adapters) → S3 (idempotent command path + crash-injection tooling) → S4 (gate assembly: Proof Sheet, SIZE/SCOPE, the proactive-set known-bads, named codes, make-surface) → harness check binding after a green run is observed (W-01 stage-2 pattern) → one probe PR (deliberately broken, RED observed, closed unmerged) → fresh-context independent verification → session close.
- **Non-scope:** S5/S6 spikes (owner-gated: Q7/Q8); Q6 transcript intake to `context/raw/` (owner-gated); Rider B/C as adoptions (stay [P] in the review artifact); Phase 3 schema work (Phase 2 exit is this session's boundary — "one phase deep", NG-04); the full constraint system, all kernel primitives, every planned known-bad (P-17: the harness must not postpone the product).
- **Grounded defaults (recorded in D-036; each overridable at any touchpoint):** Postgres as the Phase 2 real database (D-032 — Supabase is hosted Postgres; a SQLite detour would re-litigate the decided stack); Python standard library only (zero third-party dependencies — LAW-08 satisfied by construction, no lockfile yet); `psql` as the DB client (the app path and the independent verifier differ by ROLE and code path — LAW-13's spirit; no driver dependency); test-rig trust auth (ephemeral CI/local test databases only — no credential material in any file; production auth is a Phase 3+ concern, out of scope).

## 4. Results

*(sections 4–12 are appended per slice and completed at session close)*
