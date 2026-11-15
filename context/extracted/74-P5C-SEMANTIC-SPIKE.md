# Record 74 — P5-C: the semantic spike (CLAIM-082, session 49)

> STATUS: SESSION RECORD — 2026-11-15 (session 49; the banner per the standing
> records law). **Q7-GATED: the owner's budget question stays open — the slice
> opens with the deterministic parts only** (the spike's design + the
> acceptance suite's RED before any vector/embedding machinery; the gated
> parts wait for the owner's answer).

## §1 The INT ledger sync

- **INT-134..INT-147** (the standing chain): CLAIM-082 rides the standing
  Phase 5 continuation reservation INT-147 (the retroactive notation in the
  CLAIMS row at open).
- **Q7** (the owner's budget question, still open): what budget/service tier
  may the semantic spike use? Until the answer lands, this slice touches no
  external embedding service, no model download, no network budget: the
  deterministic parts only — the acceptance suite minted RED at the merged
  head `155dd8d`, the design prose (the spike's contract: what the semantic
  layer must measure, and against WHICH baseline — the P5-B corpus, exactly
  the dependency order the owner fixed).
- No new owner question opened beyond Q7 (already open).

## §2 The spike's contract (the 5C letter, one phase deep — to be elaborated at the RED)

The semantic layer exists to close the gap the keyword layer cannot: the
near-miss document (P5-B's own distractor case — the wharf/fog text that
neighbors the query's meaning but shares no token) and the synonym class
(a "quartz harbor" query that must find a "crystal quay" document). The
spike's law (the acceptance criteria the RED will pin):

- **Determinism where measurable**: the embedding of a fixed text is
  byte-stable across re-runs (or the spike refuses to ship it — the P5-B
  lesson standing: the evaluation baseline is worthless if the measure
  drifts);
- **The corpus as the gate**: every semantic admission is measured against
  `harness/runs/claim-081-p5b-eval-corpus/corpus.json` (the four case
  classes; precision/recall over the same mechanical verdict form);
- **The near-miss law**: the distractor class is where the semantic layer
  must PROVE its value — the keyword layer excludes the wharf/fog document
  by token-disjointness; the semantic layer must exclude it by MEANING, not
  by luck (a semantic layer that admits the near-miss is worse than the
  keyword layer it would replace);
- **The conflated law**: the same term spanning two documents stays BOTH-
  admitted (provenance-disambiguated, never rank-suppressed);
- **The owner boundary**: the semantic index rides the same RLS path.

## §3 The executed chain

**The RED (LAW-11, session 49):** the acceptance suite
`harness/tests/test_semantic_spike.py` minted at `155dd8d`'s merged head —
SEM-01..08 (8 pins), observed **8 FAIL / 0 PASS, exit 1** (`red-01.txt`
the transcript); the red-record bound at `42d58cd`
(`harness/red-records.json`, ARV-RED-005); the suite's registration rode
the binding commit (the ARV-RED-008 class); the binding's CI: five checks
ALL-GREEN at `939f7c4`.

**The GREEN (session 49, the deterministic parts only) — rewritten at
the D-042 round-1 repair into the HONEST form:** the machinery
`harness/semantic.py` — four arms:
- `embed` (SEM-02/03): the local deterministic map (a fixed 73-term
  vocabulary, the token-multiset -> integer-vector projection; byte-equal
  re-embeds AND content-sensitive — two different texts embed
  differently; the `--backend network` request is the typed refusal
  ARV-SEM-005 on BOTH streams — the Q7 gate's own pin);
- `verdict` (SEM-04/06/07): the semantic admission over the standing
  pack arm's own admissions, each admitted item CARRIED with its
  similarity ranking (the full-text cosine through the RLS-scoped
  get-source + blob read — the map's one honest contribution: a
  deterministic ordering of the admitted set) + the provenance field;
  the near-miss EXCLUSION is DISCLOSED as deferred (the round-1
  review's finding, repaired: no threshold over the local
  token-multiset map separates the near-miss document from the
  corpus's own — computed 0.15 vs 0.11; the verdict output says
  `near-miss-judgment=deferred-to-real-backend` on every query);
- `run` (SEM-05): the corpus run in the eval.py verdict form over the
  SAME registered corpus — the per-case VALUES pinned (R1 1/1, R2 2/2,
  N1/N2 empty=true, D1 2/2, C1 2/2, H1 1/1), the wrong-revision
  refusal ARV-SEM-002 (the EVC-10 form's own law inherited), the
  unknown-class refusal ARV-SEM-003, two-run byte-equality;
- `report` (SEM-08): the honesty line — the local map is a placeholder
  gated on Q7, NOT a quality claim; and the NEGATIVE RESULT named: the
  local map cannot make the near-miss judgment, deferred to the real
  backend.

**The D-042 round 1 (the fresh-context review): BLOCK-MERGE, eleven
findings — the two P1s: (F1) the meaning-exclusion branch was DEAD
code (the topic-registry judgment unreachable: the pack's AND law
makes every admitted item carry the probe term, so the profile is
never disjoint — the round-1 mutation M3 deleted the branch and the
suite stayed GREEN); (F2) the records and the machinery's own output
described the dead branch as the working engine. The repairs: the
dead branch deleted, the embedding WIRED into the verdict path (the
full-text cosine — F6: the embedding was decoration, never consumed),
every false claim retracted (the report arm, this record, sev), the
pins given teeth (SEM-05's per-case VALUES + two-run byte-equality +
the wrong-revision refusal; SEM-04's non-comment-line admission + the
disclosed-deferral pin; SEM-02's content-sensitivity; SEM-07's run-arm
owner pin; the revision law ARV-SEM-002; the unknown-class refusal
ARV-SEM-003; the code registry 011/012/010).**

The suite: **GREEN 8/8, exit 0** (the honest form).

**The D-042 round 2 (the fresh-context re-review): APPROVE-WITH-P2s.**
All round-1 repairs verified REAL (the dead-branch hunt: no dead code
remains anywhere in the machinery; the embedding genuinely consumed as
the full-text cosine ranking — 12 mutations, 9 bitten; the disclosed
deferral pinned by its own mutation). Two new P2s: (F-082-R2-1) the
corpus run's D1 line carried `near-miss-excluded=true` — a count-
equality tautology mislabeled as an exclusion fact under a DEFERRED
exclusion; (F-082-R2-2) the tp/fp/fn precision/recall values were
computed but unpinned (a hardcoded 1.0/1.0 passed). The repairs: the
D1 field renamed to `admitted-count-matches-expectation` with the
deferral riding the line itself; the tp=6 fp=0 fn=0 values pinned in
SEM-05. The silent-pass closure verified by value-flipping mutations
(the reviewer's originals were no-ops at this fixture: fp is 0
everywhere and D1's flag is true either way — M8b' breaks the
admitted-count arithmetic and M8c' doubles tp; both fire SEM-05).

## §4 The SEV account

The GREEN's own SEV (the Q7-gated form): the failure modes are the
5C letter's named ones — FM-01 (a semantic layer that admits the
near-miss is worse than the keyword layer it would replace; the guard:
SEM-04's two-probe form) and FM-02 (a drifting measure makes the
baseline worthless; the guards: SEM-02's byte-equal re-embeds and
SEM-03's network refusal). NOT verified: the semantic quality itself
(no external embedding, no model, no network — the Q7 gate held; the
quality claim waits for the owner's budget answer), and the D-042
review (due at this slice's PR). The measured set: the suite's own run
(GREEN 8/8), the digest-bound diff, the proofsheet re-derivation.

## §5 The close

**Merged (the INT-145 single-actor path — the #116/#117 disclosed
mechanics, exactly): PR #118 closed at the merge commit `5f31a386eb91`
(2026-11-15T13:37:12Z).** The six steps, as executed and verified:

1. the pre-change account posted at the PR BEFORE any change
   (`harness/runs/claim-082-p5c-semantic-spike/protection-pre-merge.json`,
   byte-snapshotted from the live GET and committed to the slice at
   `74397d8` before the flip: count=1, dismiss_stale=true, the 5 strict
   contexts, enforce_admins=true, force-pushes/deletions false);
2. the flip: `required_approving_review_count` 1→0 — the sole change,
   every other field byte-preserved;
3. the merge: `merge_method=merge` on PR #118 (CLAIM-082), the recorded
   message; `merged=true` verified at `5f31a38` (2026-11-15T13:37:12Z);
4. the branch deleted (204);
5. the restore: the count back to 1, every field re-PUT (200) — and
   the re-read compared **byte-equivalent: True** (count=1, the 5 strict
   contexts, enforce_admins=true, dismiss_stale=true, force-pushes/
   deletions false — the restore verified, not assumed);
6. the merge commit's five checks polled to **ALL-GREEN**; the open-PR
   count is 0.

The slice's own review chain stands as its record: the D-042 round 1
BLOCK-MERGE (two P1s — the dead meaning-exclusion branch; the records
describing it as the working engine) — all repaired in-slice into the
honest form (the embedding consumed as the full-text cosine ranking;
the near-miss exclusion DISCLOSED as the computed negative result,
deferred to Q7); round 2 APPROVE-WITH-P2s (both P1s verified real;
12 mutations, 9 bitten) — the two P2s (the D1 tautology label; the
unpinned tp/fp/fn values) closed + the closure itself verified by
value-flipping mutations (M8b'/M8c' both fire SEM-05). **GREEN 8/8**
(SEM-01..08). The successor: the PLAN's next row — Q7 (the owner's
budget answer) gates the real embedding backend; P5-E the hybrid
ranking waits on the corpus + this spike's shell.
