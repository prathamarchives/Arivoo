# REPLICATION-GUIDE — Instantiating This System in Another Project

> **STATUS: ACTIVE GUIDE (D-027(5), INT-108, 2026-10-14).** The instantiation steps for replicating this system's **pattern layer** into a new project. Owner directive (INT-108, verbatim): "Make this whole system replicable. Do not make this whole system just for Arivo. I should be able to migrate and replicate it to my other projects, so take care." Reference-tier artifact per D-022: in THIS repo it points at forms and policy homes and never outranks a root document; the portable FORMS live in `context/TEMPLATES.md`, the policies live in their canonical homes (OPERATING-MODEL §3, GLOSSARY, EXECUTION §1). In the NEW project, the contracts below become that project's own policies at its own homes — the one-fact-one-home rule travels WITH them.

## 1. What travels, what stays

| Layer | Travels? | Examples |
|---|---|---|
| Mechanisms (the pattern layer) | **YES** | entry map, intent ledger, decision register, STATE index, session memory, verifier + walls, proofs |
| Contracts/invariants | **YES** | one fact one home; append-only, supersede by reference; four decision states; evidence labels; selective read order; blocks-only-dependents scoping |
| Project content | **NO** | this repo's INT/D/Q/VER IDs, raw corpus, phase plan, product vocabulary (Work/Source/Highlight/...), Arivo-specific checks (quote fidelity against THIS corpus) |
| Arivo history | **NO** | session records, failures register, review artifacts — history is per-repo |

The seam rule (INT-108): **nothing in the system's mechanics may hardcode this repo as the only possible home.** If a mechanism only works here, it is a defect in the mechanism.

## 2. The pattern inventory (seven patterns; forms in `context/TEMPLATES.md`)

1. **Entry map** (AGENTS.md; form TEMPLATES §5) — cold-start read order + binding rules, ≤80 lines. Seed contract: the map is a map, never a brain; the read order is selective (entry → STATE → worklog tail → ledger SELECTIVE → task-relevant sources → reference tier on demand); ambiguity is reported, never compensated by reading everything.
2. **Intent ledger** — verbatim, statused owner words; the ONLY intent authority. Seed contract: append-only; unique contiguous IDs; every entry = quote + source + status; interpretations always labeled, never promoted silently; a raw/mixed corpus (if any) is preserved verbatim and never read as intent by itself.
3. **Decision register** — four states (owner decision / adopted decision / proposed recommendation / unresolved question). Seed contract: each open question names EXACTLY what it blocks (blocks-only-dependents); recommendations, presence, or elapsed time are never approval.
4. **STATE index** (form TEMPLATES §3) — five areas: position · work (active task ≠ exact next action) · dependencies (EVERY unresolved owner question) · evidence (label + ONE direct pointer per claim) · coordination (snapshot at last update, never live). Seed contract: one screen, pointers not detail, refreshed at every session exit; canonical wins on conflict.
5. **Session memory, two-tier event-typed** (forms TEMPLATES §1/§2) — every MEANINGFUL session appends a compact worklog entry (100–250 words); SUBSTANTIAL work also leaves a numbered session record (12 mandatory fields; ACTUAL commands with exit codes, never reconstructed; §1 preserves the owner's turn verbatim BEFORE the ledger entry is written).
6. **Verifier + walls** — a layer checker over the real files (one home per concern, ledger integrity, STATE freshness, raw immutability if raw exists) WITH a known-bad self-test; branch protection (PR-only, required check, strict, admins included) and a base-anchored CI judge (the required job runs the BASE's verifier over the PR head — a PR cannot weaken its own judge). Seed contract: checks are never weakened; guards are content-generic (they must not break when legitimate content changes).
7. **Proofs** — cold-start proof (uncoached fresh-context task agent + SEPARATE fresh-context grader; rubric fixed BEFORE launch; read manifest measured; budget set from the measured baseline), plus behavioral proofs for authority conflicts and unresolved-decision handling. Rerun triggers: entry point / read order / STATE schema / session protocol / authority-structure changes, and phase gates — never every doc edit.

## 3. The instantiation steps (do them in order; each has a done-when)

1. **Scaffold the entry map** — copy the TEMPLATES §5 skeleton; fill the five project fields (objective in the owner's words, repo/owner, phase, operating mode, language); write the selective read order into it. *Done when* a stranger reading only this file knows what the project is, what phase it is in, and where to read next.
2. **Start the intent ledger** — first entries verbatim from the new project's owner; pick the ID scheme; every entry carries quote + source + status. *Done when* the founding turn is ledgered verbatim and the raw source (if any) is preserved untouched.
3. **Start the decision register** — write the four-state legend; record the first adopted decisions and every open question with its blocks-only scope. *Done when* no open question is stated without naming what it blocks.
4. **Create STATE.md** — from the TEMPLATES §3 form; an honest first position ("not checked" is an honest label; an empty evidence list is a defect). *Done when* the exact next action line is true and executable by a stranger.
5. **Create the worklog + first session record** — TEMPLATES §1/§2; the record's §1 preserves the founding owner turn verbatim BEFORE the ledger entry is written. *Done when* the first session closes with the 12 fields, including real command outputs.
6. **Write the minimal layer verifier** — the checks named in pattern 6 for whatever exists so far (doc presence, ledger integrity, STATE five-area + freshness); add the self-test with known-bad mutations from day one. *Done when* `verifier` runs green AND its self-test catches every planted defect.
7. **Turn on the walls** — branch protection (PR-only, required check, strict, admins included) with the base-anchored CI judge; run a secret-isolation scan; probe BOTH rejection routes once (direct push; a deliberately broken PR) and record the observations. *Done when* both probes were observed rejected, with evidence links.
8. **Run the first cold-start proof** — TEMPLATES §4, unmodified: uncoached task agent, separate grader, read manifest, measured baseline. *Done when* it PASSES and the baseline is recorded. **A replication is proven only when this passes — not when the files exist.**

## 4. Adaptation seams (what each project decides for itself)

- Canonical language; naming of the canon set (names may change — one-fact-one-home and the authority order may not).
- Which model family runs fresh-context verification/proofs, and how host bridges import the entry map.
- What counts as "meaningful" vs "substantial" sessions (event-typed definition, calibrated to the project's cadence).
- Gates beyond branch protection (reviews, approvals, deployments) — added at their own adoption, each with an observed-working proof.
- The verifier's check set — grows with the project's mechanisms; the self-test grows with it.

## 5. Replication proof (the acceptance test for a copy)

A replication of this system is complete when, in the new repository: the cold-start proof PASSES with an uncoached fresh-context agent; the layer verifier is green and its self-test catches its known-bads; both wall rejection routes have been observed working; and the STATE index's exact next action is executable by an agent with no chat history. Anything less is scaffolding, not a replication.
