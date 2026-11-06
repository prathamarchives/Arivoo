# Record 59 — P4-A slice three: the EPUB intake (the zip/XHTML adapter by the stdlib path)

> STATUS: SESSION ENGINEERING RECORD (2026-11-06; the standing do-not-stop chain INT-134..146; D-037/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 83. PR #101 MERGED (the P4-A slice two position surface, under INT-145); the CLAIM-067 PR follows at this slice's end.

> Session 41 (2026-11-06), CLAIM-067, opened at the merged head `269921ac` (the PR #101 merge — P4-A slice two).
> Record 58 carries the position-surface account; this record carries the EPUB slice's contract + chain.

## §1 The #101 merge close (CLAIM-066 LANDED — P4-A slice two)

PR #101 (CLAIM-066 — the source-open/position surface) merged at 2026-11-06T16:53:46Z as
`269921acf8e7ab2b3cbda7408902b53460309234` under INT-145's standing authorization:

- **The five checks green at the exact final head `28e3c4b` AND on the merge commit, all observed live**
  (canonical-layer / head-tools / harness / harness-suites / harness-trusted — all success on both).
- **The merge-gate review (D-042 (1a)): `5803793140`** — the substantive host review engaging the actual diff:
  the ten-point risk surface (the save command's locked build_txn phase; the result_ref widening's losslessness;
  the substrate's hostile-write matrix; the read arm's one-statement form; the generation binding across a
  re-extraction; the delivery repair; the crash contract; the scope/size/laws; the provenance + evidence
  integrity; the three-round SEV chain), the residual risks named (the cross-site merge semantics; the
  unextracted-server arm; the EPUB coordinate mapping; the widening's external-consumer surface — none
  in-repo), and the review coverage noted (CodeRabbit skipped this head — the standing credit exhaustion;
  the host review the floor per D-042 (1c)).
- **The single-actor path:** the flip 1→0, the merge, the restore 0→1, the protections re-read
  BYTE-EQUIVALENT (all five contexts strict, admins enforced, 1 approving review, dismiss-stale, no
  force-push, no deletion); the branch deleted (204); 0 open PRs; only main on the remote.
- **No ARV-SEV-003 round at the push** — the digest bound LAST (`f7fc0edc`, validate_report GREEN; the run-dir
  artifacts excluded by the anti-self-referentiality contract) + the local trusted-gate reproduction green
  BEFORE the push (run-16, the anchored BASE driver from outside the tree, the exact S4c path the CI runs).
- **The THREE-ROUND SEV CHAIN (the slice's own account, the full reports at the runs dir):**
  - **Round 1 (agent-7c41e9d2) BLOCKED — three findings, all repaired RED-first/disclosed at `057b426`:**
    F1 (P1) THE DEAD LETTER — the claimed outbox ride was an enqueue without a delivery map: sync.py's
    `_cli_args` carried no save_position branch, so every position save's sync intent refused ARV-SYN-000 and
    the row burned retryable (observed live on the agent's own two-DB rig; the server never received a single
    save). The repair: the branch (the translated source id + the offsets — the SAME shape as the
    highlight/bookmark family) + the additive SYN-18 pin whose RED was observed at the pre-repair tree. The
    DESIGN the repair fixed to: **the site-local binding law** — the delivered save re-executes through the
    translated source id and binds the SERVER's own serving generation (each site's rows bind that site's
    generation ids, never a cross-site uuid transplant; the pin asserts the server row's generation IS the
    server's and the two sites' generation uuids differ); an unextracted server rests the row retryable with
    the command's own named ARV-POS-002 reason (a truthful state, verified with observed recovery by the
    round-2 agent's own rig). F2 (P1) the scope breach (crash.py + sync.py changed but undeclared — the
    gate's ARV-SCOPE-002/ARV-CLM-002 observed live). F3 (P3) the stale UUID comment.
  - **Round 2 (agent-9f27c4ab) BLOCKED — the repair's own class re-caught:** F4 (P1) the repair commit
    touched test_sync.py and declared only sync.py/crash.py (the same breach class, reintroduced by the
    repair — the SEV discipline working); F5 (P3) the record/STATE wording that could misread the RED as
    carrying the migration (red-01.txt honestly records 'migration 0014 present: False'); F6 (P3) the
    run-record HEAD-at-capture convention (disclosed not changed — the digests reproduce byte-exactly at the
    repair commit). All repaired at `8ba4771`.
  - **Round 3 (agent-3fa1c0d2) FINAL PASS — zero open P0/P1/P2/P3:** the gate's own scope/claim/registry
    checks green live; both red-records chains exact at every link (re-computed from git show at both ends);
    the acceptance sweep green (POS 6/6, SYN 18/18); the adversarial spot-checks 5/5 (the no-oracle
    byte-equality, the hostile-INSERT guards, the superuser mutation refusal, the generation binding); the
    leftover sweep clean (zero TODO/placeholder, zero undeclared paths, zero weakened assertions — the five
    amendments' removed lines exactly the disclosed truth-preserving forms).
- **The measured set:** the 16-record proof sheet (run-01..03 the POS suite x3 at the GREEN tree `d8a1f7a`;
  run-04/05 make verify x2; run-06/07/08 the repair tree; run-09..11 the POS suite x3 at the final tree;
  run-12 the SYN suite; run-13 make verify; run-14 the recorded PR-mode gate exit 0; run-15 the FIRST
  trusted-gate attempt exit 1 — the assembly-ordering class, KEPT as the honest observation + disclosed
  (the claim-065 run-06/F1 precedent); run-16 the green re-run).
- **What LANDED (the merged diff, `562b70f..269921ac`):** commands.py save_position (the spine's build_txn
  phase, ARV-POS-001/002/003, the `<source>@<ordinal>` result_ref); query.py get-position (ONE statement ONE
  snapshot, the no-oracle, the typed no_position_saved ANSWER, the generation binding honest across a
  re-extraction — the #99 notverified's serving-generation routing closed); migration 0014 (reading_position
  + the result_ref WIDENING UUID→TEXT with the baseline-bump 2 directive + the serving index); sync.py (the
  delivery branch + the one typed join's `s.id::text` cast); crash.py (the crash-matrix membership);
  capability.py (the surfaces row made real); test_position.py (POS-01..06, five disclosed amendments);
  test_sync.py (the additive SYN-18); the runs dir (16 records + the three SEV reports + notverified +
  proofsheet + sev.json).

## §2 The EPUB slice's contract (PLAN's elaborated P4-A slice three card; the Q8 corpus gate)

**The letter:** the `application/epub+zip` intake through the EXISTING durability ladder — the CLAIM-065
adapter registry's THIRD approved row (never a second durability path). The zip container walked by the
Python stdlib ALONE (`zipfile` + `html.parser` — ARV-DEP-008's law: no third-party dependency); the
OPF/container structure verified (the not-a-zip and no-OPF/no-container classes refuse typed); the
XHTML-derived plain-text extraction (the reflow class — the derived view the position surface composes
over, never a second position path: a position saved over an EPUB-derived view rides the same
generation binding). The typed epub-family refusals (ARV-FMT-004.., each zero-effect with the staged bytes
preserved): the not-a-zip container (a file that is not a zip at all), the broken structure (a zip without
the OPF/container chain), the unreadable XHTML set (the derived text cannot be produced). The capability
matrix's third MEASURED row over a SYNTHETIC corpus (Q8's gate — synthetic-only, never a real-EPUB
stability claim; the owner's real-document corpus is the owner gate). The encrypted/DRM class refuses
typed with the bytes staged (no circumvention surface).

**The text-access routing (the GREEN's true shape):** the blob stores the ORIGINAL bytes (content-addressed, never transformed), so the EPUB's derived text must be re-derived at EVERY text-access site — extract.py's decode (the pre-slice form decodes independently and would refuse a zip blob as ARV-EXT-002), the keyword-index full-text ride at import, the highlight/position offset validations. ONE home: formats.py's read_text(media_type, digest) — the text formats passthrough-decode, the epub walks the container, the octet-stream class refuses (the readable-text boundary stays at extraction's named refusal).

**The design boundary (the acceptance the RED pins):** the synthetic-EPUB round-trip at the real boundary
(build a zip in the test, import it, extract it, measure it — the matrix row MEASURED not asserted); the
three refusal classes each with the zero-effect + staged-bytes proof (the CAP-004 pattern); the
composition arm (import an EPUB, extract, save a position, reopen — the slice-two contract over the new
derived view, byte-identical machinery); the PDF boundary stays the following slice's (never smuggled).

## §3 The slice chain in flight

commit A (this commit: the post-#101 five-area reconciliation + CLAIM-067 opened + record 59 minted) →
the RED (test_epub.py alone at `269921ac`, tests-only per LAW-11) → the typed red-record binding → the
GREEN (formats.py's epub adapter) → the measured set (the suite x3 + make verify x2 at both trees) → the
SEV round(s) → the artifact finalize (notverified + sev.json, the digest bound LAST) → the artifact
re-bind (the PR-mode gate record + the trusted-gate reproduction) → the push → the PR → the five checks at
the exact final head → the merge-gate review (D-042 (1a)) → **the merge under INT-145** → the post-merge
verification (the five checks on the merge commit observed live) → the PDF boundary slice (P4-A slice
four) → P4-B..F → the Phase 4 exit gate — NO PAUSE EVEN FOR UPDATES (INT-146).
