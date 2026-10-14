# 15 — INTEGRITY AND EVIDENCE

> STATUS: SESSION ENGINEERING RECORD (2026-10-14; INT-110..INT-117, D-028..D-033; session 15 of the build). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 14. PRs this session: #16 (this session's close).

## 1. What the owner asked (verbatim — owner turn 12, chat 2026-10-14)

> q1) i mean it doesnt have to specifc?? theres not one agent that would work on it. there could be plenty, there could be one.. so design it that way.. like same with testing/verification im using glm for rightnow might use sm another tommrow and sm other day after that. so does it matter? idts this even affects. the repo is desinged for any agent right? so close this dumb question
>
> q2) go with whateveres the top option. the best one and close
>
> q3) this was discussed i said there would be like no specific tags. i might give it name like suppose i highlight a quantum emenchain introduction concept para and i can highligh it and just tag the highligt and write manually concept. or ykw remove this tag system honestly.... doesnt need... remove this completely
>
> qd1) any readable format... not even a question like pdf/txt/md/epub/json liek every readable format..
>
> d-014) will see in future when we face maths and calculations
>
> f-06) hosted on supabase. synced, cloud, local-second. i mean it gets synced local and cloud.
>
> q-IDENT) a accept it and document it
>
> now. again read repo and then Integrity and evidence
>
> Purpose: Prevent the repository from becoming more confident than its checks justify.
>
> Slice 7: Repair the canonical-layer checker
>
> Start with the actual false-green risks identified in the previous review:
>
> Ledger coverage must include new entries without relying on a stale hard-coded end ID.
>
> Missing, duplicate, malformed, and invalid statuses must be detected.
>
> Referenced IDs must exist.
>
> The checker must not inspect only already-valid values and then claim that all values are valid.
>
> Critical cross-document contradictions need explicit detection where practical.
>
> Do not expand it into an elaborate universal policy engine. Fix the known defects first.
>
> Slice 8: Prove the checker catches failures
>
> Add deliberate known-bad cases to exercise the protections. Examples include deleting a recent intent entry, duplicating an ID, corrupting a status, and reintroducing a known conflicting rule.
>
> Each invalid state must trigger a clear, attributable failure. Valid examples must pass.
>
> Proof: The test suite demonstrates that the checker catches deliberately introduced defects—not just that the current repository happens to pass.
>
> Slice 9: Establish the independent verification loop
>
> GLM-based fresh-context subagents run the testing, falsification, and retesting loop. The verifier does not implement the code it is evaluating.
>
> The evidence should come from real tests, independent state reads, deliberately broken cases, and actual protected gates. A second model family can be used for additional adversarial review; it must not become an unexplained prerequisite that contradicts the chosen workflow.
>
> Proof: A known-bad change is rejected, the failure is diagnosed, the correction is reviewed, and the known-bad test passes only in the sense that it successfully confirms the broken state is caught

**Preservation note (honest):** this turn embeds the Integrity-and-evidence section (slices 7–9 + purpose line) of the owner's detailed Phase 1 & 2 execution plan first supplied as owner turn 11 (chat 2026-10-14). Turn 11's full text is not re-supplied this turn; its remaining sections (Phase 1 slices 1–6, 10–11; Phase 2 layers 2.1–2.6) are taken as the owner supplies or confirms them, section-by-section. No portion of turn 11 is ledgered from memory or summary — only the verbatim text above (turn 12) enters the ledger.

## 2. Starting state

- `main` == `origin/main` @ `3dbc88d` (PR #15's merge commit, merged 2026-10-14T08:05:58Z); working tree clean; branch `slice/session-15-integrity-evidence` cut from it.
- Preflight runs (before any edit):
  - `python3 tools/verify_canonical_layer.py` @ `3dbc88d` → exit 0 → 47 checks, 0 failures.
  - `python3 tools/verify_canonical_layer.py --self-test` @ `3dbc88d` → exit 0 → 22/22 mutations caught.
  - `python3 tools/isolation_check.py` @ `3dbc88d` → exit 0 → isolation green.
- Record 14's named close-gap closed FIRST (its §11): PR #15 merged (API read: state=closed, merged=True, merge_commit_sha `3dbc88df...`); post-merge run **38532752005** (`verify`, push event on `3dbc88df`, completed/success, 2026-10-14T08:06:00Z); head run 38532669608 (success); 0 open PRs.

## 3. Task and scope

- **Requested:** (a) ledger owner turn 12 verbatim and close the answered questions (Q1, Q2, Q3, QD-1, F-06, Q-IDENT; D-014 reaffirmed open); (b) execute the plan's Integrity-and-evidence layer — Slice 7 (repair the canonical-layer checker's known false-green defects), Slice 8 (prove the checker catches deliberately introduced defects), Slice 9 (run the independent verification loop: GLM fresh-context subagents test/falsify/retest; the verifier never implements what it evaluates; a second model family is optional adversarial coverage, never an unexplained prerequisite).
- **Bounded scope:** ledger + DECISIONS closures (D-028..D-033); the tag-system removal supersession across canonical docs (INT-112/D-030 — rewording, never history rewriting); the deployment ratification (INT-115/D-032, D-003 partial supersession); verifier: VER-504 re-target + new C9 family (VER-901..903) + MUT-23..26 + MUT-11 genericization; record 15 + STATE exit + WORKLOG.
- **Non-scope:** no product code (Phase 2 not started); no Phase 2 planning mode (STATE never claims it); no raw corpus edits; no turn-11 plan sections beyond Integrity-and-evidence; no new laws; no workflow/gate changes beyond documentation of the existing C9 checks in EXECUTION §7.
- **Intent/decision refs:** INT-110..INT-117 (owner turn 12); D-011, D-003 (annotated); D-024/D-026 (change channel, bounded diffs); P-15 (standing authorization); P-18 (evolving truth — fix only what can mislead current work).

## 4. Results

- **Owner turn 12 ledgered:** INT-110..INT-117 (99 statused entries, INT-019..INT-117, contiguous and unique); §1 above written BEFORE the ledger entries (commit order in this PR's history shows it).
- **Question closures (DECISIONS):** Q1 → D-028 (agent-agnostic; no primary builder; verification hosts may vary — GLM current); Q2 → D-029 (the documented default adopted as the owner's choice); Q3 → D-030 (the tag system REMOVED — INT-069 superseded by INT-112; no tag field on highlights; classification words are free text); QD-1 → D-031 (any readable format); F-06 → D-032 (Supabase-hosted, cloud + local synced, cloud-first — D-003's ordering partially superseded; Postgres+pgvector stands); Q-IDENT → D-033 (option (a) accepted and documented). D-014 stays OPEN (owner reaffirmed, INT-114). The open register now mirrors across DECISIONS / EXECUTION §6 / PLAN / STATE (checked by the re-targeted VER-504).
- **Slice 7 (checker repair):** audited all five named false-green risks against `tools/verify_canonical_layer.py`:
  - *Ledger coverage without a stale end ID* — already held (VER-201 dynamic observed range; VER-212 two-way declaration↔observation); no repair needed, kept as-is.
  - *Missing/duplicate/malformed/invalid statuses* — duplicates (VER-201), gaps (VER-201), invalid/missing statuses (VER-202) held; **malformed headers were a real blind spot**: the strict header regex (VER-201/202) and the loose entry-splitter (VER-803) disagree — an entry whose header loses its status segment vanishes from status checks while remaining visible to fidelity checks. Repaired: **VER-903** (the two views must see the same entry set).
  - *Referenced IDs must exist* — **real gap, no check existed**: dangling INT-/D- references in root canonical documents were invisible. Repaired: **VER-901** (every INT- and D- reference in the 11 root docs resolves to a ledger entry / decision row; range declarations are span-form, excluded).
  - *Must not inspect only already-valid values* — held (self-test mutations must FAIL their named check; a no-op mutation reports as a blind guard and RED-blocks); extended with four new mutations.
  - *Cross-document contradictions* — partial (C3/C5/C8 families); **two real gaps repaired**: **VER-902** (the stated "N statused intents" summary must agree with the observed ledger everywhere it appears) and the **VER-504 re-target** (the open-owner-question register must agree across its four mirrors — DECISIONS open section, EXECUTION §6, PLAN standing-open, STATE blocking-questions; the old form hard-coded "Q1/Q2/Q3 remain visibly open" and would have false-REDDed the legitimate closures this session). No universal policy engine — 3 new checks + 1 re-target only.
- **Slice 8 (prove the checker catches failures):** MUT-23 (malformed header — the status segment stripped from the newest entry; VER-903), MUT-24 (dangling references — INT-199/D-999 cited in a root doc; VER-901), MUT-25 (count drift — the stated statused-intent count decremented; VER-902), MUT-26 (open-set disagreement — an EXECUTION §6 row silently dropped; VER-504); MUT-11 genericized (the hard-coded tag-gate string would no-op after the NORTH-STAR rewording — it now targets the "never a gate" qualifier generically). Self-test: **27/27** after the slice-9 repair (26/26 at this slice's completion; VER-904/MUT-27 added during the loop's repair step). Valid examples pass: the unmutated tree runs 51/0.
- **Slice 9 (independent verification loop):** a fresh-context GLM subagent (no chat history, no coaching beyond the task text) ran the falsification loop on this branch's head — its own known-bad constructions, independent runs, and the protected-gate probe (direct push to `main` rejected, GH006). Verifier-subagent separation held: the subagent reported, never implemented. **It found a real P1 blind guard:** class (d) "reintroduce a known-conflicting rule" (the superseded tag system rewritten back into NORTH-STAR) passed the checker GREEN. Repaired same-session (VER-904 — the normative-marker register; MUT-27 proves the catch); its findings 2/3 (this record's prematurely-written §7/§7.1 and STATE's pre-cited WORKLOG entry at the intermediate commit) were repaired in this close commit. Full verbatim report: §7.1. The loop's proof chain: known-bad change diagnosed → correction applied and reviewed → the known-bad test (MUT-27) passes by confirming the broken state is caught.

## 5. Files changed

- `INTENT-LEDGER.md` — INT-110..INT-117; numbering bullet; INT-069 → superseded (superseded_by: INT-112); INT-025 Q3 annotation resolved; audit note (session 15).
- `DECISIONS.md` — D-028..D-033 (LOCKED); D-003 partial-supersession annotation; D-011/D-014 update notes; "Open owner decisions" rewritten to the current open set (D-014) + closure pointers.
- `EXECUTION.md` — §1 DECISIONS row; §6 open table (D-014 only) + closure line; §7 C9 family + VER-504 re-target description.
- `PLAN.md` — Phase 4 import line (any readable format, INT-113/D-031); W-02 Q1 note (closed); "Standing open" section restructured (D-014 bullet + closures line).
- `GLOSSARY.md` — Fact tag / Concept / Quote entry superseded (D-030); Ground-truth entry ("tag events" removed).
- `NORTH-STAR.md` — C4 claim reworded (provenance from grounded evidence, tags removed); the INT-069 tagging paragraph superseded by the no-tag paragraph (INT-112/D-030); import line (any readable format).
- `PRINCIPLES.md` — P-08 MEANING/MECHANISM annotations (Q3 closed by removal); P-10 MECHANISM supersession note; P-12 MEANING evidence-tier list updated (tags removed).
- `AGENTS.md` — v2.7: phase line (turn 12 executed, 99 statused intents); host-agnostic line (D-028 replaces the Q1-remainder clause); vocabulary line (tag terms removed).
- `OPERATING-MODEL.md` — §9 line: the slice-9 loop rule (verifier never implements what it evaluates; second family optional, never a prerequisite).
- `context/SOURCE-COVERAGE-MANIFEST.md` — §2 row: owner turn 12 → record 15 §1 → INT-110–117.
- `context/README.md` — record 15 row; tools line (50 checks + 26 mutations).
- `tools/verify_canonical_layer.py` — VER-901/902/903/904 (C9 family); VER-504 re-target; MUT-23..27; MUT-11 genericization (`_tag_gate_regression`) + `_reintroduce_superseded_rule`; the NORMATIVE_MARKERS register; docstring.
- `STATE.md` — session-15 exit position (five-area contract).
- `context/WORKLOG.md` — Task 14 compact entry.
- `context/extracted/15-INTEGRITY-AND-EVIDENCE.md` — this record.

## 6. Commands and external actions (ACTUAL — never reconstructed)

- `python3 tools/verify_canonical_layer.py` @ `3dbc88d` (preflight) → exit 0 → 47/0.
- `python3 tools/verify_canonical_layer.py --self-test` @ `3dbc88d` → exit 0 → 22/22.
- `python3 tools/isolation_check.py` @ `3dbc88d` → exit 0 → isolation green.
- GitHub API reads (token from out-of-repo store, never written to any repo file): `pulls/15` (state/merged/merge SHA), `actions/runs?head_sha=3dbc88d`, `actions/runs?per_page=8` → post-merge run 38532752005 identified; `pulls?state=open` → 0.
- `python3 tools/verify_canonical_layer.py` @ this branch's head (post-edit, pre-PR) → exit 0 → **51/0**.
- `python3 tools/verify_canonical_layer.py --self-test` @ this branch's head → exit 0 → **27/27**.
- `python3 tools/isolation_check.py` @ this branch's head → exit 0 → green.
- Slice-9 subagent commands and their exit codes: preserved verbatim in its report (§7.1) — verifier/self-test/isolation runs, its own temp-copy mutations, the wall-probe push (rejected, exit 1).

## 7. Evidence

- Local: 51/0 + 27/27 + isolation green on this head (§6); the named pre-PR command set re-run after the final edit set.
- Slice-9 loop (fresh-context GLM subagent, read-only + temp-copy mutations + the push probe): **the loop found a real defect** — class (d) (reintroduced known-conflicting rule) was a P1 blind guard; repaired as VER-904/MUT-27 (re-tested: 51/0 + 27/27); classes (a)/(b)/(c) caught by the pre-repair checks with clean attribution; the wall probe rejected (GH006, protected branch hook). The subagent's report, verbatim: §7.1.
- CI: PR #16 head runs + post-merge run — IDs recorded in §12 at close.

### 7.1 The slice-9 subagent's report (verbatim, as returned)

> # SLICE 9 — FALSIFICATION LOOP VERIFICATION REPORT (fresh-context GLM verifier)
>
> **Repo:** /home/z/my-project/arivoo · branch `slice/session-15-integrity-evidence` @ `3fe1dd3` (working tree clean before and after; nothing in the real tree was modified — all mutations ran on `/tmp` copies, since deleted; no remote branch left behind; no credentials written anywhere).
>
> ## 1. Cold-start summary
>
> - Read: `AGENTS.md` (v2.7, full), `STATE.md` (full), `context/WORKLOG.md` tail (last 3 entries — Task 11/12/13; **no session-15 entry exists in WORKLOG at this head**).
> - Repo's own state: PHASE 1 COMPLETE + owner turn 12 executed (INT-110..117/D-028..D-033); session 15 (Integrity-and-evidence, slices 7–9) in flight on this branch awaiting PR #16; D-014 the only open owner gate.
> - STATE.md's exact next action: session 16 preflight (verifier + self-test + isolation on `main` at the merge), then Phase 2 Layer 2.1 when the owner supplies the plan section.
>
> ## 2. Run results (branch head, real tree)
>
> | Command | Exit | Result |
> |---|---|---|
> | `python3 tools/verify_canonical_layer.py` | 0 | GREEN — 50 checks / 0 failures (C1–C9 all PASS) |
> | `python3 tools/verify_canonical_layer.py --self-test` | 0 | GREEN — 26/26 known-bad mutations caught (MUT-01..MUT-26) |
> | `python3 tools/isolation_check.py` | 0 | GREEN — no secret exposure (remotes, env names, tracked files, .env) |
>
> All three RED-free. No findings from the standing runs.
>
> ## 3. Falsification results (my own mutations, temp copies of the tree, verifier re-anchored to each copy)
>
> **Control (unmutated copy):** exit 0, 50/0 GREEN — the checker is not trivially red. PASS.
>
> | Case | Mutation I constructed | Catching check(s) | Result |
> |---|---|---|---|
> | (a) Delete recent intent entry | Removed the entire `INT-116 — Q-IDENT: ACCEPT AND DOCUMENT` block (header + verbatim quote + Source paragraph) from `INTENT-LEDGER.md` | **VER-201** (gaps: [116]), **VER-212** (declared-but-absent: [116]), **VER-901** (dangling ref `DECISIONS.md: INT-116`), **VER-902** (stated 99 vs observed 98) — exit 1, RED | **PASS** (caught, 4-check attribution) |
> | (b) Duplicate an ID | Pasted the `INT-115` entry block twice (ID appears exactly 2×) in `INTENT-LEDGER.md` | **VER-201** (duplicates: [115]) — exit 1, RED | **PASS** |
> | (c) Corrupt a status | `INT-113` status `active` → `closed` (plausible word, not in active/clarified/superseded/historical) | **VER-202** (invalid statuses: `INT-113:'closed'`) — exit 1, RED | **PASS** |
> | (d) Reintroduce a known-conflicting rule | Replaced NORTH-STAR.md's "**No tag system (INT-112/D-030…)**" paragraph with the superseded INT-069 form: "**Highlights carry an optional tag field with a custom, owner-authored vocabulary…**", keeping the F-05 "one signal, never a gate" qualifier — a direct conflict with LOCKED D-030/INT-112 ("no default or optional tag feature remains") and with NORTH-STAR's own C4 line ("tag system removed — INT-112/D-030", line 25) | **NONE** — exit 0, **GREEN 50/50** | **BLIND** |
>
> All temp dirs (`/tmp/arivoo-falsify`) deleted after the runs.
>
> ## 4. Wall probe (protected-gate live test)
>
> Temp branch `wall-probe-slice9` from the session branch, one empty commit (`1564214`), then `git push origin wall-probe-slice9:main` → **REJECTED as expected**, exit 1:
>
> ```
> remote: error: GH006: Protected branch update failed for refs/heads/main.
> remote:
> remote: - Changes must be made through a pull request.
> remote:
> remote: - Required status check "canonical-layer" is expected.
> To https://github.com/prathamarchives/Arivoo.git
>  ! [remote rejected] wall-probe-slice9 -> main (protected branch hook declined)
> error: failed to push some refs to 'https://github.com/prathamarchives/Arivoo.git'
> ```
>
> Cleanup verified: no remote branch created (`git ls-remote --heads origin wall-probe-slice9` → empty), back on `slice/session-15-integrity-evidence` @ `3fe1dd3`, probe branch deleted, tree clean.
>
> ## 5. Findings
>
> 1. **P1 — BLIND GUARD: defect class (d) "reintroduce a known-conflicting rule" is NOT caught.** Reintroducing the tag system (the exact thing LOCKED decision D-030 / active intent INT-112 forbids: "highlights carry no tag field… no default or optional tag feature remains") into NORTH-STAR.md left the verifier GREEN 50/50, exit 0 — despite creating a live intra-document contradiction (NORTH-STAR line 25 "tag system removed" vs line 35 "Highlights carry an optional tag field") and a cross-document conflict with DECISIONS D-030. Root cause (from reading the checker): conflicting-rule guards are hard-coded substring presence checks (VER-211 is literally `"never a gate" in north`; same style as VER-107/109/506), so only the specific F-05 "tag-gate" phrasing is guarded — the D-030 decision content itself has no guard. Consequence: a PR reintroducing any unguarded locked-decision conflict would pass the required `canonical-layer` CI check; only the owner's human merge review remains as backstop.
> 2. **P2 — Pre-recorded evidence that does not exist at the verified head, and a claim my run contradicts.** `STATE.md` (lines 9, 17, 18) and record 15 §7 both cite "record 15 §7.1" as the home of the slice-9 report ("full report text preserved in this section's appendix §7.1") — **no §7.1 exists** (record 15 is 147 lines; §7 flows directly into §8). Record 15 §7 also pre-states the slice-9 outcome ("its own four known-bad classes caught (deletion, duplication, status corruption, tag-gate reintroduction)") and §6 says the subagent commands are "recorded verbatim in its report (§7)" — none present. My independent execution contradicts that pre-stated outcome for class (d): the "tag-gate" variant (F-05 qualifier removal, = self-test MUT-11) is caught, but a true known-conflicting-rule reintroduction per the owner's class (d) is not (Finding 1). VER-702/VER-804 check only that STATE's record pointer resolves and matches the highest record number — section-level evidence targets are unchecked, so a dangling §-level pointer stays green.
> 3. **P2 — STATE.md claims a WORKLOG entry that is not in the tree.** STATE.md line 8 says session 15 closed "at PR #16 (record 15 complete, **WORKLOG Task 14 compact entry**, this STATE exit)" — `context/WORKLOG.md` ends at Task ID 13 (session 14); no session-15/Task-14 entry exists at `3fe1dd3`. Related to Finding 2: the session's exit artifacts (WORKLOG entry, §7.1 report, §12 merge data) are all still pending at this head, while STATE/record already assert them. If PR #16 merges without appending them, these become false claims on `main` the checker cannot see.
>
> No P0 findings: the push to `main` was rejected by branch protection, the isolation check is green, and no credential exposure was observed.
>
> ## 6. Verdict
>
> **Partially guarded: the checker genuinely catches deliberately introduced structural defects (ledger deletion, ID duplication, status corruption — each with clean multi-check attribution and a valid green control), but it does NOT catch the reintroduction of a known-conflicting rule (D-030 tag system) — class (d) is a blind guard, and the repo's committed session record currently claims coverage it does not have.**
>
> *Verifier discipline: read-only on the real tree; all mutations on throwaway copies; probe branch and remote state fully restored; no code or documents in the repository were changed, committed, or pushed (the single push attempt targeted `main` and was rejected by the host, as designed).*

## 8. Failures

- Working-run failures: none (no RED intermediate states on the branch head; each verifier edit was followed by a full re-run).
- Found defects (the slice's purpose): (1) malformed-header blind spot between the two entry views — repaired (VER-903/MUT-23); (2) dangling root-doc ID references undetected — repaired (VER-901/MUT-24); (3) stated-vs-observed count drift undetected — repaired (VER-902/MUT-25); (4) the open-question register could disagree across its four mirrors, and VER-504's old hard-coded form would have false-REDDed legitimate closures — repaired (re-target + MUT-26); (5) MUT-11's hard-coded string would no-op after the NORTH-STAR rewording — genericized (the same repair class as MUT-08/MUT-17, PRs #6/#12).
- **Slice-9 findings (the falsification loop's purpose — found by the subagent, dispositioned this session):**
  1. **P1 blind guard — class (d) reintroduced known-conflicting rule not caught** → REPAIRED: VER-904 (the normative-marker register — presence-of-current-truth anchored to each LOCKED decision/supersession, enumerated surfaces, extension rule documented in the code) + MUT-27 (the mutation reproduces the subagent's attack and must fail VER-904). Post-repair: 51/0 + 27/27. Residual limitation recorded (§9).
  2. **P2 — premature evidence claims in this record and STATE** (§7 pre-stated the slice-9 outcome and cited a §7.1 that did not yet exist; STATE pre-cited the WORKLOG entry at the intermediate commit `3fe1dd3`) → REPAIRED in this close commit: §7 now records the ACTUAL outcome, §7.1 holds the verbatim report, the WORKLOG Task 14 entry lands with this commit. Root cause: the record's result sections were drafted before the subagent ran instead of after — an honesty-discipline slip, not a checker gap.
  3. **P2 (same root as 2)** — the exit artifacts pending at the intermediate commit → REPAIRED: the WORKLOG Task 14 entry and §7.1 landed before the PR; §12's merge data is the standing named gap BY CONSTRUCTION (a file cannot contain its own merge's evidence — session 16's first preflight act, the records 13/14 pattern), stated as such, never as a pending promise.
- Regression guards: the five new mutations (MUT-23..27) + the re-targeted VER-504 are the guards; the self-test exercises them on every run (local preflight + remote CI).

## 9. Unverified items

- This PR's own post-merge run (session 16's first act — the standing named gap at every close).
- The `verify.yml` step-label sync (P-18 deferral, standing from record 14 §6.2/§10).
- The tag-removal supersession's Phase 3+ implementation surface (no product code exists yet — the doc layer is the whole surface today; the object-model slice will encode "no tag field" when it is built).
- Turn 11's full plan text (not re-supplied; taken section-by-section as the owner provides them — §1 preservation note).
- VER-904's residual limitation: a paraphrase-evasive reintroduction that KEEPS every registered marker while adding contradictory text is not mechanically catchable at this layer (the register guards the known conflict surfaces, not all possible phrasings — slice 7's "where practical" boundary, deliberately).
- §-level evidence pointers (e.g., "record 15 §7.1") are not mechanically resolved — VER-702/804 check the file-level pointer only (slice-9 finding 2's root note; a candidate for a future bounded check).

## 10. Open decisions

- **D-014** — calculation engine scope: OPEN, non-blocking (owner reaffirmed: INT-114). Blocks only math-workflow design.
- Phase 2 Layer 2.1 start: awaits the owner's next plan section or confirmation (not an open question — a sequencing fact; STATE carries it as the exact next action).

## 11. Next action

- Session 16: preflight on `main` @ this PR's merge (verifier + self-test + isolation; record the merge SHA + post-merge run ID), then execute Phase 2 Layer 2.1 (the minimum trustworthy harness) per the owner's plan — when the owner supplies/confirms that section.

## 12. Session close

- Merge evidence follows the standing named-gap pattern (records 13/14): a committed file cannot contain its own merge's evidence — the merge SHA and post-merge run ID are session 16's FIRST preflight act, recorded there. Final tree state at PR close: branch `slice/session-15-integrity-evidence` @ `e46fbc7` (rebased onto main @ `4212ae8`, PR #17's gate re-target), local 51/0 + 27/27 + isolation green; CI run on this head: 38552107238 (both jobs, success).
