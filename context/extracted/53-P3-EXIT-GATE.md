# Record 53 — the Phase 3 exit gate (CLAIM-061)

> STATUS: SESSION ENGINEERING RECORD (2026-11-05; the standing do-not-stop chain INT-134..146; D-037/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 77. PR #95 MERGED this session's opening (the CLAIM-060 export/restore machine, under INT-145); the exit-gate PR follows at this slice's end.

## §1 — The #95 close (all observed live via the API)

PR #95 (CLAIM-060 — the export/restore + purge-ledger machine): the five required checks green at the exact final head `7800919` (canonical-layer 127374604712, head-tools 127374605686, harness-trusted 127374605780, harness-suites 127374605501, harness 127374605324) AND on the merge commit `3b5ed28` (canonical-layer 127377458899, head-tools 127377458789, harness-trusted 127377458637, harness-suites 127377458609, harness 127377458100); the merge-gate review D-042 (1a) `5788371151` posted 2026-11-05T16:30:49Z, thirteen seconds before the merge; the merge clean at 2026-11-05T16:31:02Z (no flip race this round — the authorization path ran its checks, the merge proceeded); the protections re-read byte-equivalent after the merge (the five contexts strict, admins enforced, 1 approving review, dismiss_stale, no force pushes, no deletions); the branch deleted; 0 open PRs; only `main` on the remote.

The CI chain: the first round at the finalize head `cf085dd` was REFUSED by the trusted gate (ARV-SEV-003 — the finalize commit's record-52 §3 account rode the reviewed set past the SEV digest; the #93/#94 digest-binds-LAST class observed a THIRD time — harness-trusted 127371777679 + harness 127371777537 failure, the other three green); the re-bind at `7800919` (the digest recomputed over the final content, the report re-validated clean, the sheet re-derived, the LOCAL trusted-gate reproduction green BEFORE the push — the exact S4c path the CI runs). CodeRabbit: skipped (the <10-stars standing state); Greptile: out of credits (the standing state); the host review floor (D-042 (1c)) carried the merge-gate review.

The session's FACT-001 recycle class (the fourth observed): the rig's data directory came up with recycled permissions (0700 lost) + the damaged `pg_notify` subdirectory — re-initdb'd from `pgbuild/rig.sh` (the rig is ephemeral test infrastructure; all state per-run from migrations); all 13 migrations applied; ARV-RIG-001 healthy.

## §2 — The gate's contract (what Phase 3 must prove, and where each proof lives)

PLAN §3.E's exit criteria, each with its evidence home at the final main `3b5ed28`:

1. Work/Source identity and Anchor contracts explicit; owner blockers resolved/isolated at exact scopes — RTM §2 (the entity contracts), §7 (the open-question boundary register: Q11/Q12/Q8's exact scopes); the Q11 baseline pinned at IMP-02/03; the Anchor contract at ANC-01..10 + the Q8 synthetic-corpus spike.
2. The real client/backend path: ingest → Highlight with valid Anchor → Bookmark → Note → keyword search — the §1.6 checkpoint (CAP-01..23), the family suites (HLG/BMK/NTE), the search arm (KWR-01..10); THE EXIT-GATE RE-PROOF: the uncoached clean-clone acceptance agent (§3).
3. The crash/restart/replay/offline fault matrices — SYS-08's matrix at SYN-01..17 (the SEV-repair pins included); the import crash matrix IMP-05..10; the capture checkpoint's two crash points.
4. Local-durable and server-durable distinct; sync's recoverable outbox states — RTM §4.2's one-commit-point law; the two outboxes (migration 0012); the state machine enforced at the substrate.
5. Every write attributed and owner-scoped; two-owner tests + independent reads — SYS-03's matrix (CAP); RLS on every authoritative table; arv_read the independent auditor (the export equality's read role).
6. Revisions immutable, tombstones work, governed purge effective after restore — HLG/BMK/NTE revision machines; EXP-08's purge-then-restore (the ledger WINS).
7. Derived passages/indexes rebuild; stale derivations never silently current — EXT's complete-or-failed generations; KWR's rebuild + the query-time tombstone parity; EXP-09's post-restore rebuild.
8. Export/restore satisfies the equality contract — EXP-01..15.
9. Every SYS requirement traces to tests + Proof Sheet evidence; every slice passing SEV; known-bads refused with named codes — RTM §1's traces + §8's slice-acceptance table; the runs dirs' proof sheets + sev.json per slice; the KB matrix.
10. Local checks + the recorded required CI checks at the final revision; THE UNCOACHED CLEAN-CLONE TASK AGENT + THE SEPARATE GRADER (no P0/P1) — §3/§4 of this record.
11. Not-verified items explicit — §5 + the per-slice notverified.txt registers.

## §3 — The uncoached clean-clone acceptance agent (SYS-09's cold-start form)

THE SETUP: a clean clone of the final main `3b5ed28` at
`/home/z/my-project/verification/acceptance-clone` (no working-tree state, no
prior sessions), two EMPTY databases (`arv_acceptance`, `arv_acceptance_2`), a
running rig, and a USER-LIKE task: set the product up from the repository's own
documentation, import a self-written essay, highlight/bookmark/note-with-
reference, find the material later, leave-and-return (a fresh process),
read the durability language of every ack, move the whole library to the
second database, and one abnormal-but-realistic event of the agent's choosing.
NO coaching: no command names, no file pointers, no schema hints — the rules
allowed reading docs freely and reading source only to understand an error,
and forbade direct SQL writes to product tables.

THE RUN (agent `agent-18f8fdca`, fresh context, full report at
`harness/runs/claim-061-p3-exit-gate/acceptance-report.md`): setup through the
repo's own surface (`make harness-health` + `make migrate` against
`PGDATABASE=arv_acceptance`, 13/13 migrations) — PASS with friction (no
user-facing README; `PGDATABASE` itself undocumented in the Makefile's
connection comment, the default silently targeting the `postgres` DB); the
walk: import (complete, digest matches) → highlight → bookmark → note with
`--ref highlight:<id>@1` (content with pipes/em-dashes/newlines round-trips
losslessly) → search finds note+source+highlight (AND semantics) → the
fresh-start reopen BYTE-IDENTICAL (`env -i` clean shell, diff-verified
snapshots) → the truthfulness read: every write ack names
`durability_rung=local_durable`, the sync status `pending=5 → acknowledged=5`
with same server refs, the restore's purge residual named honestly → the
move: export + restore into `arv_acceptance_2` — ALL authoritative reads
byte-identical + `state_hash_match=true`, PARTIAL on derived state (search
silently empty + the bookmark honestly `unresolved/no-current-generation`
until the agent re-ran extract + rebuild_keyword_index; the RESTORED ack never
names the rebuild step) → the abnormal events: the accidental duplicate
(`status=replayed`, same result_ref, zero duplicate effects), the key/body
conflict (`ARV-CMD-409`), the SIGKILL-interrupted restore (destination
provably clean, the retry converges), the repeated restore (`ARV-EXP-002`),
malformed refs/offsets (typed zero-effect refusals), the cross-owner probe
(same refusal as nonexistent — no existence oracle).

THE FINDINGS: NO P0, NO P1. Two P2s: (1) the restore leaves derived state
un-rebuilt and un-mentioned (a user-surface gap: search cannot distinguish
empty-index from no-match — P3-07's own "never a silent miss" contract — and
the ack never names the one step that moment needs); (2) no user-facing entry
doc (the CLI surface had to be assembled from `--help` + the engineering
records). Six P3s: `PGDATABASE` undocumented (+ `migrate.py --help` EXECUTES
instead of helping); import/extract acks omit `durability_rung`; the
highlight's anchor id not observable in the ordinary read (the agent missed
`get-history` — corrected by the grader); unlabeled search output; the
offset semantics (char vs byte) undocumented and the ack does not echo the
selected text; an unhandled BrokenPipeError. THE VERDICT of the user-agent:
"yes for data integrity — the most honest durability behavior I have seen in
a day-one backend; not yet a home for daily reading until the
restore→fully-operational gap closes."

## §4 — The separate grader (the all-rows walk + the acceptance grade)

TWO fresh contexts, separate from the builder and from the acceptance agent
(the independence limit stated honestly per PLAN §D-9: context labels do not
cryptographically prove independence — the design separation is the protocol's
own claim, never a proof of distinct substrates).

GRADER PART 1 (agent `agent-62dfa294`, the matrix walk —
`grader-part1-matrix-walk.md`): EVERY SYS-01..11 row walked to its RTM trace,
its named suites RUN by the grader itself against its own migrated
`arv_grader` database (all exit 0), the per-row anchor cases confirmed in its
own logs, all 13 Phase-3 slice dirs carrying non-empty proofsheet.md +
sev.json with `disposition: PASS`, one full `make verify` exit 0 (gate GREEN,
canonical 54/0), and the known-bad spot-checks (ARV-CMD-409 → CAP-12; the
uncertain-ACK → SYN-05/19; the dangling anchor → CAP-04; the corrupt blob →
CAP-15/IMP-07; cross-owner → CAP-09/11; the both-preserved sync conflict →
SYN-07; purge/restore fail-closed → EXP-07/08/10). Findings: NO P0/P1/P2 —
four P3s (a bare FAIL line in the dispatch suite's probe output; the SEV
verdict field named `disposition`; SYS-02's purge clause delivered by P3-09
while §8 maps it to P3-04/06 — consistent only with the coupling note read
along; the dispatch suite's runtime). PART-1 VERDICT: the matrix walk HOLDS.

GRADER PART 2 (agent `agent-ae8bc49d`, the acceptance grade + the FINAL
verdict — `grader-part2-final-verdict.md`): the coverage table — every
required line of §3.E covered by the acceptance run or suite-covered with the
bounded exclusion named (the tombstone/governed-purge line: no owner-facing
purge surface exists in Phase 3, the D-011 deferral, its proof requirement
suite-covered by EXP-07/10..15 run green by part 1); SEVEN independent probe
groups on the grader's own databases: (A) the full user path reproduced
(search → highlight+note+source, `digest_match=true`, the exact-span
selected_text); (B) replays + the 409 (row counts 1/1/1/1); (C) the full
export/restore reproduction (authoritative reads byte-identical; the derived
diffs named; the documented rebuild fixing them); (D) the cross-owner sweep
through ALL TWELVE read surfaces + the export (byte-identical absent-
refusals, empty lists, `rows=0` — no existence oracle anywhere); (E) the sync
walk (pending=4 → acknowledged=4, zero duplicates at the destination); (F)
the crash-interrupted restore (exit 137, zero rows, the retry converges, the
repeat refused ARV-EXP-002); (G) search-at-commit (captures searchable with
no rebuild ever run). The re-judged findings: no P0/P1 confirmed on
re-derivation; the restore P2 re-judged TWO-LAYERED — per RTM §3.7
`restored` is the CONTRACTED honest intermediate state (the ack's every claim
literally true, SYS-10's equality fully delivered — NOT a truthfulness
violation) AND a real user-surface gap (routed, not blocking); the acceptance
report's finding 5 corrected (`get-history` DOES expose the anchor_id —
verified verbatim). THE GRADER'S OWN FINDINGS: four P3s, no new P0/P1/P2.
**THE FINAL VERDICT: PASS** — the matrix walk holds, the acceptance path
covered with no P0/P1, the grader's own adversarial probes found no new
P0/P1.

## §5 — The gate verdict + the not-verified register

**THE PHASE 3 EXIT GATE: PASS at the final main `3b5ed28`.** Every §3.E
criterion walked to its evidence (§2's map); the five required CI checks
green at the final head and on the merge commit (§1); the full local
verification green at the final revision (the three recorded `make verify`
runs, exit 0, this slice's proof sheet); the uncoached clean-clone acceptance
agent completed the real user-like acceptance path with NO P0/P1; the
separate grader walked all eleven SYS rows to passing suites + complete
per-slice evidence and issued the FINAL VERDICT: PASS.

THE ROUTED REGISTER (non-blocking, each to its named home): the six grader
repairs — (1) the RESTORED ack naming the derived-rebuild step (P2; P4-00's
truthful-durability-states contract); (2) the human README (P2; P4-00's
user-facing entry); (3) `durability_rung` on the import/extract acks (P3;
SYS-01's completion, P4-00); (4) the anchor_id in get-capture (P3; P4-00's
DTO surface); (5) the offset-semantics documentation + the selected-text echo
(P3; P4-A's format-intake contract); (6) a real `--help` for migrate.py (P3;
P4-00). The standing documented residuals unchanged (the not-verified lists
of every slice; Q6-Q12's exact scopes; D-014; the OS/host separation; the
isolation undecidable classes).

THE NOT-VERIFIED REGISTER (this gate's own honest limits): the acceptance
agent and both graders ran on the same host and infrastructure family as the
builder (the independence limit — context separation is the protocol's
design, never a cryptographic proof); the acceptance path did not walk the
owner-facing purge flow (it does not exist — D-011's deferral; the proof
requirement is suite-covered); the real cross-host network surface and the
provider boundary remain Q12's (the rig's two-database model); the Phase 4+
surfaces (reader client, journal blocks, @-references resolution states,
agent reads) are NOT graded by this gate — they are Phase 4's cards; the CI
observation is the recorded API snapshot (INT-104's class — re-observed at
the merge).
