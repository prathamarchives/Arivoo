# 42 — CLAIM-051: the SEV-7 stderr-drained death classifier (P3-02's bounded follow-up)

Session 31 continuation (the standing do-not-stop chain INT-134/135/138/139/140);
the P3-01 notverified SEV-11 routing's split form, adopted at CLAIM-050 when
SIZE-002's refusal forced LAW-05's one-behavior-per-slice rule.

> STATUS: SESSION ENGINEERING RECORD (2026-10-26; intent refs INT-127/131/134/135/138/139/140; decision refs D-036/D-038/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 59. PR this session: #86 (this slice; outcome recorded only after it happens). THE SEV record for this slice: `harness/runs/claim-051-sev7-death-classifier/sev.json` (the rounds' outcome recorded there only after they run).

## 1. What the owner asked (verbatim)

The standing chain (INT-134/135/138/139/140): "work towards it ... then
P3-02..09 → the Phase 3 exit gate → P4-00 → P4-A..F → the Phase 4 exit gate —
no pause", plus the turn-36 standing instruction: "commit and push to prs
often so it doesnt disappear like this when your workspace reset".

## 2. Starting state — the post-#85 preflight

The fresh main 360b24c (PR #85 = P3-02 merged; the post-merge run 40282534114
five green; the protection restored byte-identical; 0 open PRs; the branch
deleted). make verify GREEN 54/0 at the fresh main. The CLAIM-050 close row
landed at this slice's commit A (the rule-4 form; the merge facts observed
live via the API).

## 3. Task and scope

The classifier (SEV-7's refinement): the Session's stderr pump + dead_reason
+ the _dead_exit classifier at every spine marker; the suite's restored
classifier probe + the reserved cases IMP-18/19. The scope (CLAIMS-051):
commands.py, test_import.py, red-records.json, the registry/navigation homes,
record 42, the runs dir. ONE behavior — the classifier — per LAW-05.

## 4. Results

The Session drains stderr from construction (the second daemon pump) and
dead_reason makes the death CERTAIN before the cause is read (EOF on stdout =
gone-or-going; wait(); the pump joined — never the lagging read that lost the
duplicate-key line). The classifier: duplicate-key → ARV-CMD-011 (zero
effect; retry the SAME key — the ordinal is re-read); the connection-class →
the NEW ARV-CMD-012 (the §4.1 UNCERTAIN class: the commit state is
unknowable from the client; the same-key replay resolves committed-vs-rolled-
back from the recorded state — never an assumed outcome); unrecognized → the
honest ARV-CMD-010 with the raw cause; a LIVE session raises to the stall
path (the existing 010). Wired at BEGIN/INSERTS/COMMITTED and the journal
transactions; the INSERTS block's routing comment resolved to the landed
form. IMP-18's planted-trigger arm is deterministic (no choreography, no
flake — the #83/#84 lesson family); IMP-19's killed-backend probe is
deterministic (the backend terminated in-build, before BEGIN — notverified
item 2 names the true-mid-commit-partition residual). The suite: 22 cases
GREEN (three consecutive runs); make verify GREEN 54/0 over the spine
re-wiring (the capture suite's CAP-21 real-race arm still classifies 011 —
from the drained stderr now). Source adds 87/400.

## 5. Files changed

harness/commands.py (the Session pump + dead_reason; _DUP/_CONN/_dead_exit;
the marker wirings; the _journal_txn classifier); harness/tests/test_import.py
(the restored probe + IMP-18/19 in their validated pre-split forms);
harness/red-records.json (the amendment); CLAIMS.md (the 050 close + the 051
row); STATE/AGENTS/PLAN/WORKLOG (the re-derivation); this record; the runs
dir (scope, red-01, the proof set, notverified, the sheet, sev.json).

## 6. Commands and external actions (ACTUAL — never reconstructed)

- The RED: python3 harness/tests/test_import.py at 360b24c → exit 1,
  ARV-TEST-000 (the classifier absent; red-01.txt); the branch pushed at the
  RED commit (3d505cd) and PR #86 opened EARLY per the standing instruction.
- The GREEN: the classifier landed at 917dc64 (the suite 22/22, three
  consecutive runs; make verify GREEN 54/0); pushed.
- The proof set: run-01 (the suite 22/22) run-02..12 (the eleven machinery
  suites, all exit 0) run-13 (make verify, exit 0); the PR-mode gate's
  RECORDED green run and the sheet's assembly land with the post-round
  finalize (the round-1 F2 repair: the first finalize's assembly call failed
  silently on the not-yet-written notverified path, making its "the sheet
  assembled" claim false — caught by the round-1 reviewer, the sheet now
  actually assembled and the gate green recorded).
- The merge sequence: the five checks observed green at the head; the
  single-actor bar reproduced (422/405); the flip; the merge; the RESTORE;
  the post-merge run; the branch deletion — all recorded at §12 on merge.

## 7. Evidence

The runs dir: scope.txt, red-01.txt (the machinery-absent RED), the proof
set, the sheet (assembled with the post-round finalize), the notverified's
seven boundaries, sev.json (the rounds' record, written only after they run). The red-records chain: the
CLAIM-050 binding + the CLAIM-051 amendment (the probe + the restored cases,
the RED observed at 360b24c).

## 8. Failures (each honestly recorded, each repaired in-slice)

None at the implementation (the classifier's forms were VALIDATED at the
pre-split tree 3230330 and restored verbatim — the first run of the restored
suite was green; the rehearsal lesson of the lost session paying its
dividend). The ROUND-1 findings (agent-8fe337ac, BLOCKED): F1 the '24 cases'
count was FALSE (22 — codes conflated with cases; corrected across the
homes; the two immutable commit messages carry the error and this note is
its only honest correction) + F2 the finalize claimed the sheet assembled
while the assembly call had failed on the not-yet-written notverified path
(the claim false; the sheet now actually assembled at the post-round
finalize) + F3 STATE's Phase line malformed by the re-derivation's stale
tail (repaired in the same pass).
The digest-binding lesson from CLAIM-050 (reviewed_diff_sha256 reads the
blobs AT HEAD; the sheet's SEV section embeds the report digest) is applied
HERE from the first step: the sev re-bind runs only AFTER the content commit,
and the sheet re-assembles after every re-bind.

## 9. Unverified items

The notverified's seven boundaries (the substring-phrase classification; the
true mid-commit partition residual; the classifier's epistemic limit; the
catastrophic-host pump class; the frozen vocabulary's preservation; the
CI-host standing class; the routed follow-ups).

## 10. Open decisions

D-014 + Q6–Q12 unchanged (the classifier touches none of them).

## 11. Next action

The SEV rounds (every finding RED-first-fixed or reasoned-no-fix in-PR,
every thread dispositioned BEFORE resolution) → the CodeRabbit round →
merge under D-042 (the 405 bar → the recorded flip → RESTORE) → the
post-merge five-check run + the branch deletion + the protection re-read →
**P3-03 (Extraction generation and Anchor + the Q8 anchor-stability spike) →
P3-04..09 → the Phase 3 exit gate → P4-00 → P4-A..F → the Phase 4 exit
gate** — NO PAUSE (INT-134/135/138/139/140).

## 12. Session close

The push-early discipline standing; the PAT rotation reminder stands for the
project's completion; the worklog's host-side mirror carries Task 59. The
routed follow-ups remain recorded and never lost (notverified item 7).
