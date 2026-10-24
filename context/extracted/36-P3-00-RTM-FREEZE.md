# 36 — P3-00: the requirements/interfaces/schema freeze (CLAIM-043)

> STATUS: SESSION ENGINEERING RECORD (2026-10-24; intent refs INT-134/135/138/139; decision refs D-011/D-021/D-030/D-032/D-039/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 52. PRs this session: PR #78 (this slice; outcome recorded only after it happens). THE SEV record for this slice: `harness/runs/claim-043-p3-00-rtm-freeze/sev.json` (sheet_section TRUE — the first section-bearing committed Proof Sheet; the CLAIM-042 transition completing).

## 1. What the owner asked (verbatim — the standing chain)

> "start working towards phase 3 and phase 4 do not stop as a world class systems and software engineer" (turn 34 — preserved at record 35 §1; INT-139)

No new owner turn arrived with this slice; the standing do-not-stop chain (INT-134/135/138/139)
executes the documented order (D-039/D-041/D-043): H-02 complete at PR #77, so **P3-00 is the
next bounded slice** — the Phase 3 entry gate: "No product schema migration until this gate is
accepted" (PLAN's card). No owner question is opened or closed by this slice (RTM.md §7 keeps
D-014/Q6–Q12 visible at their exact scopes).

## 2. Starting state

Main `647591b` (the PR #77 merge, 2026-10-24T12:15:15Z; post-merge run `40093172762` five
green, observed); the branch deleted; protection restored and verified byte-identical (1
review, dismiss_stale, strict, five contexts, admins, rcr, no force, no deletions); 0 open
PRs; `make verify` GREEN at the fresh main (53/0). The #77 review legs all closed: the three
CodeRabbit round-1 Minors fixed in-PR with posted dispositions; the round-2 outside-diff Minor
dispositioned by explicit SEV-4 reference; Greptile's trial-credit absence NOTED. An honest
boundary note recorded: the REST branch-DELETE endpoint returned 404-masking (the branch
existed; the git-side `push --delete` path worked and the deletion was confirmed by the 404
follow-up) — the API-side quirk recorded, the deletion itself verified.

## 3. Task and scope

CLAIM-043 — P3-00: the requirements/interfaces/schema freeze. Scope: `RTM.md` (new root
canonical doc), `EXECUTION.md` (the §1 fold, FX-07), `PLAN.md` (the P3-00 status), `STATE.md`,
`AGENTS.md`, `CLAIMS.md`, `tools/verify_canonical_layer.py` (ROOT_DOCS + VER-806),
`context/WORKLOG.md` (Task 52), `context/extracted/36-P3-00-RTM-FREEZE.md`, the slice's runs
dir.

## 4. Results

**THE RED (red-01.txt, observed live at the predecessor):** the NEW VER-806 — the ONE-RTM
contract (D-039 element 3) made mechanical — fails with every PLAN.md SYS requirement (11
rows) untraced and RTM.md absent; the canonical verifier exits 1 naming all eleven ids. The
spec-slice's discriminating RED is the freeze's absence itself; the guard is defect-bound
(P-17): a future SYS row without its RTM trace fails the layer, and the RTM's absence is a
named refusal, never a silent gap.

**RTM.md — the freeze (the fix):** the ONE requirements traceability matrix at its single
canonical home, never duplicated into navigation files: §1 the SYS-01..11 traces (each: the
requirement pointer to PLAN's row, the owning component, the frozen interfaces, the
PRE-REGISTERED test paths — the suite/case shapes named before the implementation slices run —
the claim ladder, the user validation scenario); §2 the authoritative entity contracts
(Work, Source, ExtractionGeneration, Anchor, Highlight, Bookmark, Note, CommandLog — the
identity/ownership/actor/revision/provenance shape on the 0002/0003 substrate conventions;
the derived-state rule; the P4 reservations clearly labeled as reservations); §3 the seven
state machines (import, capture, revision/tombstone/purge, local outbox, server sync
application, indexing, export/restore) with exclusive, observable, fail-closed states; §4 the
transaction/acknowledgment semantics (commit-before-ack; one commit point; the frozen rung
vocabulary; the Q12-neutral content-addressed blob adapter); §5 the migration/compatibility
plan; §6 the named-failure matrix; §7 the open-question boundary register — each question's
EXACT boundary against the freeze, with the Q12 comparison table (Supabase Storage vs
S3-compatible vs DB-bytea across the nine criteria PLAN names) and the Supabase Storage
recommendation explicitly labeled evidence-preparation for the owner's gate, NEVER a
ratification; §8 the P3 slice acceptance trace (which RTM rows each slice closes).

**THE GREEN:** VER-806 PASS (11/11 traced); VER-901 PASS over the TWELVE root canonical
documents (RTM.md's INT-/D- references all resolve — the new doc bound by the reference
checks in the same commit it joins ROOT_DOCS); the canonical verifier exits 0.

**THE Q-BOUNDARY DISCIPLINE:** the freeze adopts only the registered BASELINES (Q11: no
auto-merge, no identity uniqueness, byte-reuse ≠ logical identity; Q12: the provider-neutral
blob adapter, no provider name in the schema, no cross-store atomicity claim; Q8: the
synthetic corpus default with the real-corpus claim gated). No question is closed, narrowed,
or promoted (VER-504's mirrors unchanged: DECISIONS/EXECUTION/PLAN/STATE).

**THE SECTION-BEARING SHEET:** this slice's sev.json sets `sheet_section: true` — the FIRST
real section-bearing committed Proof Sheet, exactly as the CLAIM-042 transition named (the
base 647591b renders sections; the trusted leg re-derives the section-bearing sheet). The
SEV-3 follow-up (the base-side mechanical expectation) is assessed at this slice's review and
recorded in the sev.json's findings.

## 5. Files changed

`RTM.md` (new), `EXECUTION.md` (§1 row), `PLAN.md` (the P3-00 status + pointer),
`tools/verify_canonical_layer.py` (ROOT_DOCS + VER-806), `STATE.md`/`AGENTS.md` (the
post-#77 truth, Phase 3 EXECUTING), `CLAIMS.md` (the open row), `context/WORKLOG.md` (Task 52),
this record, the slice's runs dir (red-01, the proof set, sev.json, the sheet).

## 6. Commands and external actions (ACTUAL — never reconstructed)

- `python3 tools/verify_canonical_layer.py` → exit 1 at the RED commit (VER-806 naming all 11
  untraced ids) → exit 0 at the fix head (VER-806 PASS; VER-901 over 12 docs)
- `make verify` → exit 0 at the fix head (the PG rig env exported in the same invocation —
  the record-35 lesson held)
- The proof set captures + the RECORDED PR-mode gate green (the exits in the sheet)
- The base-compat simulation: the BASE's proofsheet (647591b) re-derives this slice's
  committed SECTION-BEARING sheet byte-identically (the opt-in transition's completion proven
  in the exact form the trusted job runs)
- API: the PR opened; the review rounds observed at the PR (never pre-recorded here)

## 7. Evidence

red-01.txt (the VER-806 RED); the proof records + the section-bearing sheet (PASS ARV-PRF-004
at the gate); the sev.json (the four-wing trace over SYS-11/01/02/03 rows; the findings with
dispositions; the honest not-verified list; sheet_section true); VER-901's live scan of the
new doc's references; the CLAIMS row.

## 8. Failures (honest)

- No in-slice walls catch this time beyond the standing environment discipline: the rig env
  exported in every shell (the record-35 §8 lesson applied, no repeat); the ledger/claims
  edits append-only (the record-35 INT-138 slip class: no repeat). The honest boundary note
  from §2 (the REST DELETE 404-masking) is recorded, not a slice failure.

## 9. Unverified items

- The freeze is ACCEPTED through this slice's review + merge; the independent phase-gate
  grader walks the matrix at the Phase 3 EXIT gate (never claimed done here).
- The Q11/Q12/Q8 baselines remain owner-gated at their exact scopes (RTM.md §7); the Q12
  recommendation awaits the owner's ratification — nothing in the frozen contracts depends
  on the choice (the neutral adapter isolates it).
- The state machines and test paths are PRE-REGISTERED contracts; their proofs land with the
  implementation slices (P3-01..09) — this slice freezes, it does not implement.
- The remote CI's five-check run at this PR's head — observed at the PR.
- The N12 residual unchanged; the standing documented residuals unchanged.

## 10. Open decisions

None new; none closed. D-014 + Q6–Q12 at unchanged scopes (RTM.md §7 records the boundaries;
VER-504's four mirrors agree).

## 11. Next action

Merge the CLAIM-043 PR (#78) once review-complete (D-042: the per-thread read-and-disposition
pass BEFORE any resolution; the single-actor bar → the flip path), then **P3-M0 (the
migration oracle) ∥ P3-K0 (the kernel primitives) → P3-01 (the kernel + first real command —
the §1.6 capture checkpoint as early as possible) → P3-02..09 → the Phase 3 exit gate** — NO
PAUSE (INT-134/135/138/139). The SEV-3 follow-up (the base-side sheet_section expectation)
lands as its own bounded slice if this slice's review adopts it.

## 12. Session close

This record is written at the slice's finalize commits (the SEV-6 discipline: the covered-path
content first, the record over the committed tree, the proof set + the RECORDED gate green,
the sheet re-derived over every record — now carrying its SEV section). The standing
do-not-stop chain continues into P3-M0/P3-K0 the moment #78 merges.
