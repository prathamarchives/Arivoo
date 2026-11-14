# Record 72 — P5-A: the authorized retrieval API / context packs (the Phase 5 opening)

> STATUS: SESSION ENGINEERING RECORD (2026-11-14; the standing do-not-stop chain
> INT-134..147 — the continuation into Phase 5, INT-147's reservation at this
> commit A; D-037/D-041/D-042/D-043). Historical process artifact per D-022:
> NOT owner intent, outranks nothing. Worklog entry: Task 96. PR #114 MERGED
> (P4-F — the Phase 4 exit, under INT-145); record 71 §3/§4/§5 closed at this
> commit (the staged close riding the next claim's commit A — the #113-close
> pattern; PR #115 the gate-refused record-only carrier, closed honestly).

Session 46 (2026-11-14), CLAIM-080, opened at the merged head `bf8be3a` (the PR
#114 merge — P4-F, the Phase 4 exit). Record 71 carries the P4-F close complete
(§3/§4/§5 closed at this commit); this record carries the Phase 5 opening —
P5-A, the authorized retrieval API / context packs.

## §1 The pre-Phase-5 gate (D-034) — the classification-words rule, verified explicit

The gate's letter (owner turn 13 disposition, record 16 §1, the review's P2
disposition): "the classification-words rule must be made explicit before Phase
5 begins — ordinary user text is processed as text; classification words
('concept', 'fact', 'quote') receive no special tagging behavior or dedicated
weighting unless the owner decides otherwise (D-030's removal carried to its
semantic conclusion); VER-211/MUT-11 are rewritten then to enforce the
clarified rule, not the older tag-feature wording."

**Verified explicit at this commit A, the three surfaces:**

1. **The mechanic (the code identity):** the keyword index's tokenizer
   (`commands.py:_kwr_tokens`) treats EVERY word uniformly — case-folded whole
   tokens under `re.UNICODE`, CJK single-character + run tokens, deduplicated
   per document. No weighting, no rank, no `ts_rank`, no setweight, no special
   casing of any word class: the index stores a token SET per document and the
   search matches whole tokens only (the AND intersection; the deterministic
   (kind, entity_id) ordering — `query.py` SEARCH_SQL). A "concept", "fact",
   or "quote" in the owner's free text is a token exactly like any other. There
   is no tag field anywhere (D-030 removed it; the highlight row carries
   selected text + anchor only).
2. **The wording (the authority files):** NORTH-STAR.md's tag-system paragraph
   (2026-10-13/14) already carries the clarified rule — "a classification word
   ... is free text the owner writes manually if they want — never a structured
   feature, never imposed ... the owner's free-text words, if present, are one
   signal, never a gate: unclassified highlights still feed provisional
   discovery." PLAN.md's pre-Phase-5 gate line carries the same. VER-211/MUT-11
   (the marker checks protecting the older tag-feature wording) were retired
   with the wording they protected — no mechanic remains to rewrite: the
   marker's object (the tag-feature text) no longer exists.
3. **The Phase-5 carrying law:** every retrieval surface this phase builds
   (P5-A first) inherits the rule as a TESTED law — the retrieval arms never
   special-case a word class, and the classification-word law is pinned in the
   P5-A suite (a probe: a document seeded with the classification words scores
   and ranks identically to the same document with them replaced by ordinary
   words — no dedicated weighting anywhere in the pipeline).

**The gate is satisfied; Phase 5 begins at this claim.**

## §2 The P5-A contract (the PLAN 5A row, elaborated one phase deep at the #114 landing)

**The letter (the PLAN 5A row):** "Authorized retrieval API/context packs —
keyword/identity/filter/temporal/behavioral queries, pagination, strict
budgets; MCP wraps the same core; every item carries source/revision/anchor +
trust status + mechanically true why; imported content untrusted — an embedded
instruction cannot widen scopes or mutate state; explicit truncation retaining
provenance."

**The design boundary (one phase deep at the #114 landing):**
- **The retrieval core widened (the query arms):** harness/query.py's read
  surface gains the 5A forms over the LANDED families — the identity lookups
  (the existing get-* arms ARE the identity rung; the pack assembly composes
  them), the filter/temporal/behavioral query forms (list arms widened with
  the temporal filters over the landed event surfaces — the reading sessions'
  dwell windows, the capture history's timestamps; the behavioral queries =
  the reading-state/journal-history composition), pagination (the existing
  keyset `--after` law, never offset), strict budgets (the response budget as
  the read budget's deepening — record 69 §2's named Phase 5 increment: the
  pack assembly bounded by byte/row budgets with the typed truncation, never
  a silent drop).
- **The context pack (the named deliverable):** ONE pack call assembling the
  bounded, provenance-carrying material for a query — each item carrying its
  source id/revision, its anchor (for the source-bound families), its trust
  status (the imported-content law: source material is UNTRUSTED text; an
  embedded instruction in it is data, never an instruction — the pack never
  executes content), and the mechanically true why (the exact matching terms /
  the identity path / the filter predicates that admitted the item — emitted
  by the machine that did the admission, never an LLM's narration).
- **The explicit truncation law:** a pack over the budget truncates at the
  item boundary, records WHAT was truncated (the count and the total), and
  retains the provenance of every retained item — never a silent drop, never a
  mid-item cut.
- **The MCP surface wraps the same core** (the standing law from CLAIM-078:
  the wrapper adds NO retrieval logic — the pack arms join the tool registry
  as the 5A arms over the same query.py).
- **The bounded exclusions:** no semantic/vector retrieval (P5-C/P5-D under
  Q7's owner gate); no ranking changes (P5-B's eval corpus comes FIRST — no
  relevance ordering beyond the existing deterministic ordering); no
  relationship candidates (P5-F); no concept formation (P5-G); no write arms
  (the agent path stays READ-ONLY structurally); no cross-owner material ever.

## §3 The executed chain

(In flight — appended at the rounds.)

## §4 The SEV account

(In flight — appended at the rounds.)

## §5 The close

(Appended at the merge.)
