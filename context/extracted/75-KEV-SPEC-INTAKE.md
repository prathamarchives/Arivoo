# 75 — KEV SYSTEM-ENGINEERING SPEC INTAKE (CLAIM-083)

> STATUS: SESSION ENGINEERING RECORD — IN PROGRESS (session 50, 2026-11-16; owner turn 43, INT-148; §1 preserved verbatim below BEFORE any ledger entry was written; D-022: historical process artifact, NOT owner intent, outranks nothing). PRs this session: #119 (CLAIM-083, disposition: open → merged under INT-145's single-actor path).

## §1 — the owner's turn, verbatim

The turn arrived as an IM message carrying one attachment: the Kev system engineering specification. The message text (the owner's typography preserved, including the caps and the compound sentences):

> REAOSN THROUGH THIS DOC AND EXTRACT THE CONTEXT AND INTENT AND REASON THROUGH IEM STEP BY STEP AND UNDERSTAND AND CLEAN UP AND ORGANIZE THE REPO AND KEEP IT UP TO DATE WITH EVERYTHING. AND PLAN MODE IS WHEN YOU DONT TAKE ACTION AND REASON PROPERLY AND PREPARE A EXECUTION PLAN AND KEEPS REFINING UNTIL MET USER EXCEPTATIONS
>
> and after ruthless reaosning nd understanding the implementing it

> start now implementing dont stop until done

Attachment disposition:

1. `KEV_SYSTEM_ENGINEERING_SPEC (1).md` — **the operative spec (1,905 lines), preserved verbatim at `context/raw/KEV_SYSTEM_ENGINEERING_SPEC.md` (SHA-256 `4eceb21cc508de6f4d3886eefd5208af8c5903887ecb7bcab9aa0eb6f3a05dfc`); the extract below cites its sections, never rewrites them.**

The turn's two halves, as received in sequence: (1) the plan-mode instruction — reason through the spec, verify against the live repo read-only, produce a refined execution plan, mutate nothing — executed in the plan session (the Kev Execution Plan deliverable, 2026-11-16); (2) "start now implementing dont stop until done" — the execution directive this record carries. The plan session's deliverables live outside this repository (the sandbox's `download/` area, per the host contract); this repository receives the INTAKE: the verbatim spec + this record + the ledger's owner-intent entries + the question registrations. The implementation of the spec itself (the Kev repository, its Phases 0–9) is a NEW repository's work (the spec's own §2.1: a new, separate repository to be created for Kev) — never this repository's scope.

## §2 — the intake's contract (what this slice is and is not)

**Is:** the verbatim preservation of the owner-supplied spec into `context/raw/` (the manifest-registered, hash-anchored form — the 3.txt precedent class); the owner-intent ledger entries (INT-148 the turn itself; INT-149 the session reservation for the Kev-execution chain); the Kev-owner-question registrations (Q13/Q14/Q15, all four mirrors — they extend, never close, the standing D-014/Q6–Q12); the navigation updates (STATE/CLAIMS/PLAN/WORKLOG/AGENTS); the riding of the parked CLAIM-082 close records (the recycle-precedent RESUME form).

**Is not:** an adoption of the spec's architecture into Arivoo. The spec's §2.2 integration rule is binding: no guessed Arivoo table or interface enters any contract — every integration surface is discovered from the live repository. The spec's §17.7: Kev's write surface must be built by a bounded Arivoo-side change under this protocol when its 5F row lands — never bypassed. LAW-29 stands: no generative model runs inside Arivo's pipeline; the two-repo split (the spec's own §2.1 requirement) is the compliance mechanism, and this repository's Phase-5 rows (5D–5J) proceed under their own gates unchanged.

**The dependency shape (the spec's own roadmap, verbatim-faithful):** Kev's P0 contract freeze and P1 Supabase foundation have no Arivoo dependency; Kev's P2 event intake consumes the ALREADY-LANDED `arv.server_outbox` surface (migration 0012, P3-08/CLAIM-059); Kev's P3 reads call the ALREADY-LANDED P5-A pack API (CLAIM-080, PR #116); Kev's P5 first autonomous write waits for Arivoo's 5F row (the candidate-relation surface) and is gated by 5H (the Kev policy/evaluation gate — the PLAN's own turn-20 dependency correction). The one hard gate between the tracks: 5H passes BEFORE any Kev-backed evidence promotion, 5G graduation, or graph compounding.

## §3 — the extract (the spec's operative skeleton, section-mapped)

The full text is the authority at `context/raw/KEV_SYSTEM_ENGINEERING_SPEC.md`; this extract is a map, never a replacement. Section by section:

- **§0 + §0.1** — the executive definition and the ten non-negotiable principles: autonomous maintenance/creation; no routine approval prompts; no model-owned database authority; no unsupported facts promoted; no loss of original material; no provider lock-in; no blocking the owner's workflow; no silent destructive actions; uncertainty explicit; external material distinguishable.
- **§1–§4** — the operational model (five responsibilities: creation, organization, discovery, maintenance, improvement), the repository boundary (Kev = new separate repo), the Arivoo baseline snapshot the spec was written against (5A/5B/5C landed; the outbox and the retrieval API as its named integration surfaces — both verified still-landed at main `5f31a38`), and the architecture (event-driven, harness-controlled, provider-independent; the owner writes in Arivoo, Kev processes asynchronously).
- **§5** — the four subsystems: event intake (transactional outbox → queue → task state machine), retrieval/context (typed client, bounded packs, evidence spans, hostile-content labeling), decision (structured recipes with evidence + uncertainty), and action (bounded write tools through stable Arivoo interfaces; the autonomy policy matrix).
- **§6–§9** — the model strategy (primary + backup providers, free-API-first, small fast reasoning models), the knowledge-contract schemas (conceptual only — Arivoo's migrations are the real schema home), the provenance/evidence discipline, and the tool catalogue (typed, bounded, validated).
- **§10–§15** — Supabase provisioning (project `arivo`, org `catalyst`, ap-south-1; do-not-delete the inactive `meraki`/`phase 0`/`catalyst.exe` projects — owner-gated), the event/intake contracts, the task engine, the evaluation discipline (corpus with held-out split; arbitrary real text + engineered edge cases — resolving the repo's Q8 default toward the owner's stated direction), the V-model/RTM discipline, and the engineering standards.
- **§16–§17** — the nine phases (0–9, ordered by demonstrable capability not calendar) and the execution protocol (claim-before-work, RED-first tests, definition-of-done, evidence classification — the same shape this repository's protocol already enforces; the ticket list BOOT/ARCH/DB/EVT/ARV/CTX/MDL/DEC/POL/ACT/EVAL/OBS).
- **§18–§25** — risks, mitigations, observations, self-improvement, validation, completion criteria, and the owner-decision list (§21.1 verbatim below in §4; §21.2's Phase-0 confirmations mapped to Q13–Q15).

## §4 — the owner decisions the spec carries (the verbatim decision block, spec §21.1)

> - Model provider selection and model names (primary and first fallback)
> - Exact Supabase organization and region at provisioning time; the current proposal is organization `catalyst`, Mumbai `ap-south-1`
> - External research scope at first
> - Whether to keep the existing Supabase projects or retire them
> - Repository visibility for Kev (private recommended by the spec, pending owner confirmation)
> - Identity of the single owner entity, authorization mapping, and any operational boundaries
> - Evaluation corpus governance and the held-out split policy

The three that are OWNER-only decisions this repository can register but not take: model provider (Q13), Supabase project confirmation + existing-projects disposition (Q14), external-research scope (Q15). The others (repo visibility for Kev — private per the spec's own recommendation, owner-gated; owner identity/authorization; corpus governance) carry spec-stated defaults or are Kev-repo-internal registrations.

## §5 — the close

(to be completed at the merge)
