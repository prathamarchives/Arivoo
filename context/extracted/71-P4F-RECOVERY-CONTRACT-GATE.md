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

(In flight — appended at the rounds.)

## §4 The SEV account

(In flight — appended at the rounds.)

## §5 The close

(Appended at the merge.)
