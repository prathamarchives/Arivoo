# PROOF SHEET — slice claim-069-p4b-client-acceptance (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 30d3358acfa107a3215c98c9f676b2d531add220
- generated (last record's timestamp): 2026-11-06T21:20:54.991652+00:00
- run records: 7

## Run records (command, exit, output digest)
- `python3 harness/tests/test_client_acceptance.py` -> exit 0 · output sha256 11579301a80617f3 · 2026-11-06T20:51:12.806186+00:00
- `python3 harness/tests/test_client_acceptance.py` -> exit 0 · output sha256 11579301a80617f3 · 2026-11-06T20:51:17.523687+00:00
- `python3 harness/tests/test_client_acceptance.py` -> exit 0 · output sha256 11579301a80617f3 · 2026-11-06T20:51:31.536087+00:00
- `make verify` -> exit 0 · output sha256 29de0bdc4520d268 · 2026-11-06T20:57:30.210387+00:00
- `make verify` -> exit 0 · output sha256 8153cfe4cbf5a1ad · 2026-11-06T21:03:35.295005+00:00
- `env SLICE=claim-069-p4b-client-acceptance GATE_DIFF=origin/main make gate` -> exit 0 · output sha256 c83d4d997e80c086 · 2026-11-06T21:20:24.776540+00:00
- `env ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-069-p4b-client-acceptance python3 -I /home/z/my-project/verification/anchored/trusted_gate_anchored.py --repo /home/z/my-project/Arivoo --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 0 · output sha256 19800828d8bb1db6 · 2026-11-06T21:20:54.991652+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- NOT VERIFIED — the honest limits of CLAIM-069 / P4-B slice one (the
- client-shaped adversarial acceptance path; LAW-04; never empty-by-omission).
- WHAT THIS SLICE PROVES: the clean EXTERNAL client driver (harness/client.py
- — P4-F's named proof vehicle) over the landed API: the full user walk
- (import -> extract -> the first open's truthful no_position_saved -> save
- position -> highlight -> bookmark -> note -> the reopen round-trip, every
- ack frozen) + P4-B's named adversarial conditions each pinned to its typed
- refusal or truthful answer — the no-oracle on BOTH paths, the four DTO laws,
- the lost-ack convergence, the idempotency, the reload durability, the
- generation binding honest across a re-extraction, the tombstone lifecycle —
- through subprocess invocations of the real CLIs only (no privileged path, no
- SQL, no role: the same surface the separate reader-client repo will call).
- THE HONEST LIMITS (including the SEV round's four P3 notes, routed/recorded
- — never silently dropped):
- - NO READER-CLIENT UI (the bounded exclusion, held): the driver is the
- BACKEND's proof vehicle — a scripted client, not the product UI. The
- reader client is P4-B's SEPARATE authorized repo (the owner's gate); no
- client UI work is claimed here.
- - THE FORMAT-LAW ARM'S ZERO-EFFECT OBSERVABILITY (the SEV round's P3-1):
- the CLI-observable counters (list-captures / list-notes / the position's
- ordinal) are INSENSITIVE to a source import — a successful import also
- leaves them unchanged, and no CLI enumerates sources, so a client cannot
- observe the import refusal's zero effect beyond the typed refusal itself
- (which IS pinned: the refusal + the journal's failed-retryable state are
- the landed contract). The suite's "row counts unchanged across all four"
- wording overstates that one arm — the counts prove zero effect for the
- NOTE/HIGHLIGHT/POSITION refusals, not the import refusal.
- - THE CRASH ARM'S VOCABULARY (P3-2): the driver's docstring names
- commands.py/extract.py/query.py and omits crash.py (the crash-injection
- helper used by CAC-04's lost-ack arm — the established CLAIM-066/NTE-06
- injection vocabulary; all observations remain client-obtainable, the
- crash point is test-side). Disclosed.
- - THE CAC-09 SCAN'S NARROWNESS (P3-3): the no-privileged-path law's
- mechanical scan is a token tripwire (the database tool name, the role
- names, the SQL verbs) — the law's SUBSTANCE was verified by the SEV
- reviewer's full-file read (every subprocess target is a repo CLI; never a
- shell, never an eval). A wider scan (more tokens, AST-level) is a
- hardening follow-up.
- - THE SCRATCH-DIR LITTER (P3-4): the driver's mkdtemp scratch dirs are
- never cleaned (a /tmp litter per run — cosmetic, never a correctness
- issue; the cleanup is a small follow-up).
- - THE CONDITIONS ARE THE BACKEND'S VIEW OF THE CLIENT: the nine conditions
- pin what the BACKEND honestly answers; the actual client's UX decisions
- (retry policies, UI states, offline queues) are the separate repo's own
- surface — never claimed here.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 9cc50df40ef1e93cf08eb4f71493a4a17d03ad6cfef87ee4ac5813c5e525f939
- reviewed_diff_sha256: b9b397f0beb576b2d3f19d56ed134bcfc31b6794238707426940798ebf179325
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 1

## Assembly
- sheet sha256 (of the content above, excluding this line): 4c0e665a9ed78eaee2cb5ae3e6787ff304910a924c7a2f8a22182d4752f4d020
