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

**The GREEN (session 49, the deterministic parts only):** the machinery
`harness/semantic.py` — four arms:
- `embed` (SEM-02/03): the local deterministic map (a fixed 73-term
  vocabulary, the token-multiset -> integer-vector projection; byte-equal
  re-embeds; the `--backend network` request is the typed refusal
  ARV-SEM-005 on BOTH streams — the Q7 gate's own pin);
- `verdict` (SEM-04/06/07): the semantic admission over the standing
  pack arm's own admissions — the meaning judgment through the topic
  registry (a probe's target topic vs the admitted item's topic profile;
  the near-miss note names the meaning-neighbor cluster WITHOUT
  fabricating an admission — the exclusion is meaning-driven); the
  conflated law (both=true, the provenance field on every line); the
  owner boundary (the standing RLS path — the spike never re-implements
  retrieval);
- `run` (SEM-05): the corpus run in the eval.py verdict form over the
  SAME registered corpus (per-case, precision/recall, the JSONL run
  record in this slice's runs — the EVC-10 form exactly);
- `report` (SEM-08): the honesty line — the local map is a placeholder
  gated on Q7, NOT a quality claim; what it proves is the determinism
  and the verdict form the real backend must inherit.

The suite: **GREEN 8/8, exit 0**.

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

(Appended at the merge.)
