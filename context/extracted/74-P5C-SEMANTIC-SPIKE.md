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

(The next session's work: the RED at `155dd8d`'s merged head — tests-only,
LAW-11; then the GREEN; then the measured set; then the D-042 review at
this slice's PR.)

## §4 The SEV account

(To be written at the GREEN.)

## §5 The close

(Appended at the merge.)
