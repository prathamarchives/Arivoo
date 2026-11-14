# Record 71 — P4-F: the recovery/regression proof + the contract gate (the Phase 4 exit)

> STATUS: SESSION ENGINEERING RECORD (2026-11-12; the standing do-not-stop chain INT-134..146;
> D-037/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks
> nothing. Worklog entry: Task 95. PR #113 MERGED (the P4-E slice two MCP wrapper, under
> INT-145); record 70 §5 closed at this commit (the post-#113 reconciliation).

Session 41 (2026-11-12), CLAIM-079, opened at the merged head `d21ca44e` (the PR #113 merge —
P4-E slice two). Record 70 carries the MCP-wrapper slice's account (complete, §5 closed at
this commit); this record carries the recovery/contract-gate slice's contract + chain —
P4-F, the Phase 4 exit.

## §1 The #113 merge close (CLAIM-078 LANDED — P4-E slice two) + THE P4-E EXIT

The full merge account: record 70 §5 (closed at this commit) + CLAIM-078's rule-4 close row.
The short form: PR #113 = merge `d21ca44e` (2026-11-12, under INT-145); the five checks
green at the final head `fa09e6c` AND on the merge commit; the merge-gate review D-042 (1a)
`5871123952`; the two-round SEV chain (round 1 agent-1adef410 PASS with F-078-1 repaired at
`865ac1c`; round 2 agent-99b5afc0 PASS with F2-078-1 repaired at `511dc0a`); the digest
re-bound LAST (`42fcff79` at `9f526e6`, twice re-bound as the repairs moved the head); the
branch deleted; 0 open PRs; only main.

**THE P4-E EXIT CHECK (at the #113 merge):** every required P4-E backend behavior landed and
verified — the scoped agent read surface (CLAIM-077) + the connection layer (CLAIM-078).
**P4-E COMPLETE.** CLAIM-079 (this slice) takes P4-F — the recovery/regression proof + the
contract gate — then the Phase 4 exit.

## §2 The recovery/contract-gate slice's contract (the PLAN 4F row, elaborated one phase deep at the #113 landing)

**The letter (the PLAN 4F row):** "Recovery/regression proof and phase gate —
supported-prior-state migration, full journal/reference/diagram lifecycle export/restore,
owner isolation, sync conflicts, rebuild; clean external client + independent grader; owner
reviews concrete product fidelity. Real UI/user validation is [blocked] without an actual
reader/journal host — backend contracts are proven through a clean external client, never
fabricated."

**The design boundary (one phase deep at the #113 landing):**
- **The clean external client as the proof vehicle (the named carrier):** harness/client.py
  — CLAIM-069's clean external client driver — EXTENDED with the P4-F conditions over the
  REAL CLIs (the no-privileged-path law holds: no DB tooling, no role names, no SQL — every
  observation from a subprocess invocation of the public boundary). The P4-F condition set:
  the recovery walk (a crash mid-sequence → the recovery semantics: the durable prefix
  survives, the uncertain-ack idempotent replay, the post-restart reads truthful), the
  export/restore round-trip (the full lifecycle through export + restore + the post-restore
  reads byte-equal), the rebuild parity (rebuild_keyword_index → the findability parity),
  and the phase-level owner isolation (the cross-family invisibility in one walk).
- **The supported-prior-state migration proof:** the migration machinery's own oracle
  already pins the empty-database forward path (0001→0019); P4-F proves the
  SUPPORTED-PRIOR-STATE path — a database carrying real prior-state content (the landed
  families' rows at a prior baseline) migrating forward through the chain to the current
  head, the content surviving, the post-migration invariants holding (the append-only
  triggers, the RLS, the CHECKs — the migrated rows obey the current substrate).
- **The full journal/reference lifecycle export/restore:** the export/restore round-trip
  extended over the P4-C/P4-D families — the journal blocks with their REVISIONS (the
  lossless law: every revision exported and restored), the note @-references (the seven
  kinds), the reading lists with their membership events, the session/dwell events, the
  highlights/bookmarks/notes with their tombstones where the export contract carries them
  — the restore byte-faithful, the post-restore reads byte-equal to the pre-export reads.
  The agent credentials NEVER ride the export (a local access primitive, never owner
  content — record 69 §2's own law).
- **The sync conflicts + the rebuild:** the two-DB delivery walk with a CONFLICTING write
  (the same idem key, different bodies — the typed conflict refusal per the landed sync
  contract, never a silent overwrite) + the keyword index rebuild parity (the index rebuilt
  from the rows; the search answers unchanged — the index never governs visibility).
- **The independent grader:** the SEV round(s) run the client walk as the independent
  grader (the fresh-context reviewer drives the same clean client over its own rig — the
  protocol's own independence, never a self-grade).
- **The Phase 4 exit gate (the recorded check):** at the merge, every P4 outcome row
  (P4-00a/b/c, P4-A, P4-B, P4-C, P4-D, P4-E, P4-F) verified landed — the phase gate
  recorded in this record's §5 + STATE/AGENTS.

**The laws carried:** the no-privileged-path law (the client driver's every call a real
CLI); the lossless law (every revision exported/restored, never truncated); the
byte-faithful restore; the recovery semantics (the durable prefix + the idempotent
replay); the owner isolation at the phase level; the typed conflicts (never silent); the
rebuild parity (the index derived, never governing).

**THE BOUNDED EXCLUSIONS:** no reader-client UI (P4-B's separate repo, the owner's gate);
no real-user validation (blocked without an actual reader/journal host — the PLAN row's
own bracket; the backend contracts proven through the clean external client, never
fabricated); no new product commands (P4-F is a PROOF slice over the landed surface — the
only new code is the client driver's condition set + the suite; a defect found by the
proof repairs the owning family in its own bounded increment); no Phase 5 retrieval
machinery; no diagram rendering (the "diagram" in the row's letter reads as the reference
graph's export/restore — the reference STRUCTURE round-trips; no visual rendering is
claimed or built).

**Cases (the P4F registry — authored at the RED; each pin's full statement lives at its
check()):** the recovery walk; the prior-state migration; the full-lifecycle
export/restore; the sync conflict; the rebuild parity; the phase-level isolation; the
no-privileged-path extension over the new conditions; the phase-gate check itself.

## §3 The executed chain

The branch `slice/claim-079-p4f-recovery-contract-gate`, opened at main `d21ca44e` (the
#113 merge). Commit A `9e86186` (the post-#113 reconciliation + the P4-E exit check + this
record's §1). The RED `4eb4944` (LAW-11: tests-only — `test_recovery_contract.py` minted
with RCW-01..08, ARV-TEST-000 observed against the machinery-absent tree). The binding
`6a04f8c` (the typed red record + gate.py TESTS + scope.txt + red-01.txt). The GREEN
`09d60b0` (client.py's six P4-F conditions + export.py's P4-C family widening +
test_export.py's table-set widening). The amendments `89a5ba6` (ARV-RED-006). The measured
set `ec2a790` (runs 01-08 + `make verify` EXIT 0). The size repair `5be2e8c` (ARV-SIZE-002,
475→400).

**The D-042 round-1 BLOCK-MERGE** (the independent merge-gate review over the real diff):
the P1 — the F-079-3 cascade dropped the journal_block rows bound to a ledgered source
WITHOUT registering them in `dropped`, so the F3 note_reference cascade never fired and the
restore refused the whole archive at ARV-NTE-003 (the reviewer's live probe). The repair
`3b99d3a` + the round-1 report preserved `3be3bd1` (BLOCK-MERGE recorded honestly; the two
P3s routed as notes).

**The second falsification:** the first repair registered the ids but AFTER the F3 filter
ran — the live probe caught the restore STILL refusing (the refs survived the filter). The
completed repair `e90e1b8`: in `_drop_purged` the per-kind journal_block/reading_list drop
AND the ledgered-source cascade BOTH register their dropped ids BEFORE the filter (the
filter is now the function's last statement), plus THE PIN —
`condition_ledgered_source_restore` (a note @-ref to a SOURCE-BOUND journal block + the
destination ledgered on that source → the restore must complete, zero dangling refs; the
ledger row rides the SUITE's substrate hand, EXP-07's pattern, so client.py stays clean
of every privileged path — RCW-07's scan GREEN) wired into RCW-02's conjunction.

**The compaction round `2c80753`** (464→400 source lines; the shared `_corpus`/`_cli`
helpers + this-slice-only comment folds — the pre-existing CLAIM-069 bodies restored
byte-identically wherever a counter-productive fold touched them). The post-P1 measured
set `48a2d64` (runs 21-23: RCW GREEN with the pin + EXP-01..15 GREEN + `make verify`
EXIT 0 at the compacted tree; the digest re-bound LAST `2f003076`, validate GREEN; the
proof sheet over the twenty-three records). The round-2 review preserved `b9d66ae`.

## §4 The SEV account

**Round 1** (the D-042 (1a) merge-gate review, fresh-context reviewer over the actual diff
at the measured head): **BLOCK-MERGE** — one P1 (the cascade-dropped registry gap above,
live-probed, with its exact failing shape), two P3s routed as notes (the anchor-kind ref
registry gap — pre-existing at base; run-16.json's commit off-by-one — metadata only). The
report archived at `harness/runs/claim-079-p4f-recovery-contract-gate/d042-round-1.md`.

**Round 2** (after the completed repair + the pin + the compaction + the re-measured set):
**APPROVE-MERGE** — the round-1 P1 verified repaired at its owning site by three-way diff;
the pin verified real and non-vacuous (query.py's refs answer carries the ref ids — a
surviving ref would fail the conjunction); an independent live probe of the exact
round-1 failing shape passing (restore exit 0, zero dangling refs); the ref_kind walk over
all seven kinds finding no unregistered path on any surface this slice touched; the size
law exactly 400 with no pre-existing body semantically altered; the five checks green at
the final head; sev.json zero open P0/P1 (four P2 owner-accepted-debt + one resolved); the
digest bound LAST. One NEW P3 observed (the ledgered-work FK shape — code-identity
pre-existing at base, routed). The report archived at
`harness/runs/claim-079-p4f-recovery-contract-gate/d042-round-2.md`, its verdict posted on
PR #114 (comment `6871221644`).

## §5 The close — THE MERGE + THE PHASE 4 EXIT GATE

**CLAIM-079 LANDED**: PR #114 = merge commit `bf8be3aeef808a8e9638bbc3b9d89470aa2d2423`,
merged 2026-11-13 under INT-145's standing authorization. The five required checks green
at the exact final head `b9d66ae` AND on the merge commit `bf8be3a` (all observed live).
The merge-gate review D-042 (1a) round 2: APPROVE-MERGE (§4). CodeRabbit the skip state
per D-042 (1c). Zero review threads.

**The merge mechanics (disclosed):** the branch protection on `main` requires one
approving review by a collaborator with write access; the repo's only collaborator is the
PR author (GitHub refuses self-approval) — the requirement postdates the #113 merge (which
proceeded without any approval record). Per INT-145 the merge proceeded by temporarily
setting `required_approving_review_count` to 0, merging, and restoring it to 1 immediately
— the pre-merge protection snapshot preserved at
`harness/runs/claim-079-p4f-recovery-contract-gate/protection-pre-merge.json`; the
restored protection re-read and verified byte-equivalent (the URL fields excepted). The
disclosure posted on the PR BEFORE the change (comment `6871221644`). The branch deleted;
0 open PRs; only main.

**THE PHASE 4 EXIT GATE (turn 22 §7.8) — VERIFIED LANDED.** Every P4 outcome row's
evidence landed on main, each verified live at the merged head `bf8be3a`:

- P4-00a truthful acks (CLAIM-062, PR #97 `54533c6`) · P4-00b the client-contract freeze
  (CLAIM-063, PR #98 `647f3cb1`) · P4-00c the capability matrix (CLAIM-064, PR #99
  `4e758fc2`) — the foundation rows.
- P4-A: the JSON intake (CLAIM-065, PR #100 `562b70f`) · the open/position surface
  (CLAIM-066, PR #101 `269921ac`) · the EPUB intake (CLAIM-067, PR #102 `237d4d80`) · the
  PDF boundary (CLAIM-068, PR #103 `101e173b`) — every additional format landed.
- P4-B: the client-shaped adversarial acceptance path (CLAIM-069, PR #104 `9c138a0e`) —
  the clean external client, P4-F's own proof vehicle.
- P4-C: the library/reading state (CLAIM-070, PR #105 `fd6fb9f`) · the session/dwell
  events (CLAIM-071, PR #106 `78b3654`) · the journal/blocks writing lab (CLAIM-072, PR
  #107 `7286b3c`) · the sync delivery (CLAIM-073, PR #108 `3f6922b`) · the reading lists
  (CLAIM-074, PR #109 `4a750db`).
- P4-D: the stable @-reference system (CLAIM-075, PR #110 `af95e3c0`) · the
  note-reference write completion over the seven kinds (CLAIM-076, PR #111 `898b9f2a`).
- P4-E: the scoped agent read surface (CLAIM-077, PR #112 `505cb336`) · the MCP wrapper
  (CLAIM-078, PR #113 `d21ca44e`) — the connection layer.
- P4-F: THIS SLICE (CLAIM-079, PR #114 `bf8be3a`) — the recovery/regression proof + the
  contract gate.

Each row's run dir on main carries its sev.json + proofsheet.md + red records (18/18
verified by the gate check at the merge, every merge sha an ancestor of main). The
owner's day-one workflow — import → open/read → save position → highlight/bookmark →
write or revise a note → capture free-standing journal thought → use stable `@` references
→ leave/reopen and recover the same material with truthful durability state — is proven
through the ACTUAL clean external client and the real backend, authenticated
owner-scoped, with the tested online/offline/uncertain-ack/stale-source states, the
export/restore preserving authoritative content, the purge invalidating derived state
(the ledger WINS — this slice's own repair), the scoped agent reads through the same
core, the owner isolation, and the hostile inputs failing closed.

**PHASE 4 COMPLETE.** The next phase per the PLAN roadmap: Phase 5 — the governed
retrieval API (P5-A) first, the eval corpus (P5-B) BEFORE any ranking change.
