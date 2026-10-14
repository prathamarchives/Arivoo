#!/usr/bin/env python3
"""verify_canonical_layer.py — the canonicalization-layer verifier (Layer-0 gate precursor).

Proves the canonicalization conditions (INT-068) plus the review-merge session's drift
gates (INT-091/D-024, F-01) against the REAL repository files — not a manually written
report (LAW-01's spirit applied to documents). Exit 0 = green; every failure prints rule
ID, violation, and repair path (diagnostics contract). Pure stdlib (LAW-08 pre-Phase-1).

Usage:
  python3 tools/verify_canonical_layer.py               # verify the real tree
  python3 tools/verify_canonical_layer.py --self-test   # apply known-bad mutations to a
                                                        # temp copy and prove each guard
                                                        # FAILS (KB-01..06 spirit: the
                                                        # guards are themselves tested)

Conditions checked:
  C1  a fresh agent loads the Intent Ledger + STATE + governing docs from the read order
  C2  every active requirement traces to owner intent or an adopted decision;
      the ledger's ID range is contiguous, unique, fully statused, and consistent with
      its own numbering note (DYNAMIC — no hard-coded end; F-01 repaired: entries past
      INT-068 can no longer vanish, and a truncated tail cannot pass)
  C3  D-004 and the old The List wording no longer conflict with D-015 and P-16
  C4  the archive is clearly historical; raw is not mistaken for owner-only intent
  C5  one canonical home; Q1–Q3 visibly open; consent is scoped; GLM verification is
      governing (F-02/F-03); D-024 recorded
  C6  this verifier proves it on the real files (this run IS the proof)
  C7  the garden: STATE.md live and pointing at real targets, FAIL-001 recorded with a
      known-bad, review artifacts in context/reviews/ (D-024)
  C8  the coverage control (F-09/D-025): source-coverage manifest complete; raw corpus
      SHA-256-anchored (AUT-02 at C3); every ledger quote mechanically validated against
      its cited raw source (fabrication and transcription drift are caught); STATE.md's
      record pointer is fresh (never stale)

Ref: /EXECUTION.md §7. When the harness exists (Phase 2), these checks move up the
ladder into `make audit` (LAD-01).
"""

from __future__ import annotations

import re
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

EXPECTED_RAW = [
    "0.txt",
    "1.txt",
    "2.txt",
    "3.txt",
    "Arivo Agent Execution Specification.md",
    "engineering transcript.txt",
    "upstream of engineering transcripts.txt",
]

# NOTE (sub-agent finding 2, 2026-10-14): the BRIEFS list was static and went stale the
# moment session record 12 landed — the F-01 failure class recurring inside the verifier
# itself. VER-205 now scans the directory dynamically; every *.md in context/extracted/
# must carry a status banner, whatever its number.

STATUSES = ("active", "clarified", "superseded", "historical")
INT_HEADER = re.compile(r"^\*\*INT-(\d{3})\s+—\s+(.*?)\s+—\s+(.*?)\*\*\s*$", re.M)


class Layer:
    """Runs all checks against a repo root (the real tree or a mutated copy)."""

    def __init__(self, repo: Path):
        self.repo = repo
        self.results: list[tuple[str, bool, str]] = []

    def read(self, rel: str) -> str:
        path = self.repo / rel
        if not path.is_file():
            return ""
        return path.read_text(encoding="utf-8")

    def check(self, code: str, ok: bool, what: str, fix: str = "") -> None:
        self.results.append((code, ok, what if ok else f"{what} — FIX: {fix}"))

    def failed(self, code: str) -> bool:
        return any(c == code and not ok for c, ok, _ in self.results)

    # ------------------------------------------------------------ C1: boot
    def c1(self) -> None:
        agents = self.read("AGENTS.md")
        order = [m.group(1) for m in re.finditer(r"^\s*\d+\.\s+`/?([^`/]+\.md)`", agents, re.M)]

        def pos(name: str) -> int:
            for i, entry in enumerate(order):
                if name in entry:
                    return i
            return -1

        li, ns, ex, st = (
            pos("INTENT-LEDGER.md"),
            pos("NORTH-STAR.md"),
            pos("EXECUTION.md"),
            pos("STATE.md"),
        )
        self.check(
            "VER-101",
            li != -1 and ns != -1 and li < ns,
            f"read order: INTENT-LEDGER.md (#{li+1}) loads before NORTH-STAR.md (#{ns+1})",
            "AGENTS.md read order must list /INTENT-LEDGER.md first — the owner words load before any understanding forms (INT-068)",
        )
        self.check(
            "VER-106",
            st == 1 and (self.repo / "STATE.md").is_file(),
            f"read order: /STATE.md is step 2 (found #{st+1}) and the file exists at root — the current-state index (D-024)",
            "add /STATE.md as read-order step 2 in AGENTS.md and create the file (D-024; F-08: cold start must surface an exact next action)",
        )
        self.check(
            "VER-102",
            ex != -1,
            "read order includes /EXECUTION.md (the canonical execution-contract home)",
            "add /EXECUTION.md to the AGENTS.md read order (D-021)",
        )
        self.check(
            "VER-103",
            "verbatim owner material" not in agents
            and "mixed owner statements" in agents
            and "Never edit it" in agents,
            "AGENTS.md: context/raw/ described as the mixed verbatim corpus (not owner-only), never edited",
            'AGENTS.md must carry the D-022 wording: raw = "mixed owner statements, AI analysis, and pasted documents; never edit"',
        )
        self.check(
            "VER-104",
            "ONLY through INTENT-LEDGER" in agents,
            "AGENTS.md: the intent rule — intent enters only through the ledger",
            "AGENTS.md binding rules must state the intent rule (EXECUTION.md §2)",
        )
        self.check(
            "VER-105",
            0 < len(agents.splitlines()) <= 80,
            f"AGENTS.md is a map, not a brain ({len(agents.splitlines())} lines, MEM-03 limit 80)",
            "split AGENTS.md — detailed knowledge moves to authoritative homes",
        )
        self.check(
            "VER-107",
            "NEVER land on `main` directly" in agents and "explicit authorization" in agents,
            "AGENTS.md: the change-channel rule — review/analysis/proposal artifacts never land on main directly (D-024)",
            "restore the change-channel binding rule (D-024, FAIL-001's guard at C6)",
        )
        self.check(
            "VER-108",
            "update `/STATE.md`" in agents and "EVERY meaningful session" in agents,
            "AGENTS.md: session exit updates STATE.md and every meaningful session leaves a numbered record (INT-072 broadened, F-04)",
            "restore the session-exit rule: STATE.md refresh + a numbered session record for every meaningful session",
        )
        self.check(
            "VER-109",
            "GLM-based subagents" in agents and "INT-070" in agents,
            "AGENTS.md: test/verification loops run on GLM-based subagents (INT-070 governing)",
            "restore the GLM verification rule (INT-070; F-03)",
        )

    # ------------------------------------------------------------ C2: ledger
    def c2(self) -> None:
        ledger = self.read("INTENT-LEDGER.md")
        headers = INT_HEADER.findall(ledger)
        ids = [int(i) for i, _, _ in headers]
        dups = sorted({i for i in ids if ids.count(i) > 1})
        lo, hi = (min(ids), max(ids)) if ids else (0, 0)
        gaps = [n for n in range(lo, hi + 1) if n not in set(ids)]
        self.check(
            "VER-201",
            not dups and not gaps and lo == 19,
            f"ledger IDs are unique and contiguous across the OBSERVED range INT-{lo:03d}..INT-{hi:03d} ({len(ids)} statused entries) — dynamic, no hard-coded end",
            f"duplicates: {dups}; gaps: {gaps}; expected start 19 — backfill or repair the ledger (AUT-02; F-01: entries past any frozen bound must never vanish)",
        )
        bad_status = []
        for i, _, raw in headers:
            word = raw.split("(")[0].strip().lower()
            if word not in STATUSES:
                bad_status.append(f"INT-{int(i):03d}:'{word or '(missing)'}'")
        self.check(
            "VER-202",
            not bad_status,
            f"every ledger entry carries a valid status ({'/'.join(STATUSES)}) — parsed leniently, invalid or missing statuses are caught",
            f"invalid statuses: {bad_status} (AUT-02; F-01: the old regex was blind to bad statuses)",
        )
        self.check(
            "VER-203",
            "INT-001..INT-018" in ledger and "never recycled" in ledger,
            "ledger documents the reserved INT-001..018 range (v1 spec IDs not in corpus — never recycled)",
            "keep the numbering note in INTENT-LEDGER.md",
        )
        self.check(
            "VER-204",
            "superseded (superseded_by: INT-030)" in ledger,
            "the one corrected owner statement (INT-051 AIOS-to-DB) is preserved with its superseded_by link",
            "INT-051 must keep its text, status, and superseded_by pointer (AUT-03)",
        )
        banner_fail = []
        extracted_dir = self.repo / "context" / "extracted"
        briefs_on_disk = sorted(p.name for p in extracted_dir.glob("*.md")) if extracted_dir.is_dir() else []
        for b in briefs_on_disk:
            text = self.read(f"context/extracted/{b}")
            has_banner = ("STATUS:" in text[:600]) or ("SUPERSEDED" in text[:400])
            if not has_banner:
                banner_fail.append(b)
        self.check(
            "VER-205",
            not banner_fail and len(briefs_on_disk) >= 11,
            f"all {len(briefs_on_disk)} extracted briefs and session records on disk carry a status banner (dynamic scan — new records can never be silently exempt, the sub-agent-found F-01 recurrence)",
            f"add the banner to: {banner_fail} (D-022 — future agents must not mistake history for active decisions)",
        )
        north = self.read("NORTH-STAR.md")
        self.check(
            "VER-206",
            "INT-019" in north and "day-one intake" in north,
            "NORTH-STAR: import is an explicit day-one intake requirement traced to INT-019 (D-023)",
            "NORTH-STAR first-usable-workflow must carry the import requirement",
        )
        self.check(
            "VER-207",
            "INT-068" in ledger and "canonicalization" in ledger.lower(),
            "the canonicalization directive itself is ledgered (INT-068)",
            "record the owner directive that authorized this slice",
        )
        self.check(
            "VER-208",
            "read repo, prs, review the reviews, merge" in ledger,
            "the review-merge directive is ledgered verbatim (INT-091 — the authorization basis of D-024)",
            "record owner turn 7 verbatim in the ledger (INT-091)",
        )
        self.check(
            "VER-211",
            "never a gate" in north,
            "NORTH-STAR: tags are one signal, never a gate for concept formation (F-05, INT-069/P-10 compatibility)",
            "restore the F-05 qualifier — untagged highlights still feed provisional discovery; no system-owned labels",
        )
        bullets = re.findall(r"-\s\*\*INT-(\d{3})(?:\.\.INT-(\d{3}))?\*\*", ledger)
        named: set[int] = set()
        for a, b in bullets:
            start, end = int(a), int(b) if b else int(a)
            named.update(range(start, end + 1))
        declared = {n for n in named if n >= 19}  # 001..018 are reserved-absent by design
        observed = set(ids)
        undeclared = sorted(observed - declared)
        missing_declared = sorted(declared - observed)
        self.check(
            "VER-212",
            not undeclared and not missing_declared,
            "the numbering section and the entry headers agree both ways (every declared range ≥ 019 is present; every observed entry is declared) — a truncated tail cannot pass",
            f"headers with no numbering declaration: {undeclared}; declared but absent: {missing_declared} — the ledger and its numbering note must move together (AUT-02; tail-truncation class)",
        )

    # ------------------------------------------------------------ C3: register
    def c3(self) -> None:
        decisions = self.read("DECISIONS.md")
        d004 = next((ln for ln in decisions.splitlines() if ln.startswith("| D-004 ")), "")
        self.check(
            "VER-301",
            "SUPERSEDED" in d004 and "D-020" in d004,
            "D-004 is marked superseded-by-D-020 (text preserved, status annotated)",
            "annotate D-004's status cell — never rewrite its text (AUT-02/03)",
        )
        d020 = next((ln for ln in decisions.splitlines() if ln.startswith("| D-020 ")), "")
        self.check(
            "VER-302",
            bool(d020)
            and "refinement-debt register" in d020
            and "REMOVED from the register" in d020
            and "P-16" in d020,
            "D-020: The List = refinement-debt register; semantic/pgvector/vector-search removed to the active sequence; P-16 invariant",
            "D-020 must exist and reconcile D-004 with D-015/P-16",
        )
        gloss = self.read("GLOSSARY.md")
        the_list = next((ln for ln in gloss.splitlines() if ln.strip().startswith("- **The List**")), "")
        self.check(
            "VER-303",
            "refinement-debt register" in the_list and "can never enter" in the_list,
            "GLOSSARY: The List defined as the refinement-debt register with the P-16 invariant",
            "update the GLOSSARY The List entry (D-020)",
        )
        reg = self.read("context/extracted/07-ON-THE-LIST.md")
        closed = reg.count("CLOSED: in the active sequence")
        live_ok = "ACTIVE MECHANISM" in reg and "L-001" in reg
        self.check(
            "VER-304",
            closed >= 3 and live_ok and "refinement-debt register" in reg,
            "the register: L-001 live (sync only); L-002..L-004 closed as in-active-sequence",
            "07-ON-THE-LIST.md must reflect D-020 — semantic capabilities are in the sequence, not deferred",
        )
        principles = self.read("PRINCIPLES.md")
        self.check(
            "VER-305",
            "refinement-debt register" in principles,
            "P-07 mechanism cites the refinement-debt register (no deferral framing)",
            "update P-07 MECHANISM to the register language",
        )

    # ------------------------------------------------------------ C4: archive
    def c4(self) -> None:
        readme = self.read("context/README.md")
        self.check(
            "VER-401",
            "seven files" in readme and "3.txt" in readme,
            "context/README names seven raw files including 3.txt (stale count corrected)",
            "context/README.md must list the actual corpus",
        )
        self.check(
            "VER-402",
            ("mixed archive" in readme or "mixed owner statements" in readme)
            and "NOT owner-only intent" in readme
            and "NEVER edited" in readme,
            "context/README: raw = mixed archive, not owner-only intent; never edited",
            "context/README.md must carry the D-022 source-tier wording",
        )
        self.check(
            "VER-403",
            "slice F-01" not in readme and "F-01 " not in readme,
            "context/README migration reference no longer points at the superseded F-01 step",
            "migration trigger = corpus closure (FX-07), not the F-band",
        )
        raw_files = sorted(p.name for p in (self.repo / "context" / "raw").glob("*") if p.is_file())
        self.check(
            "VER-404",
            raw_files == sorted(EXPECTED_RAW),
            f"context/raw holds exactly the 7-file verbatim corpus (unchanged: {len(raw_files)} files)",
            "the raw corpus is immutable — AUT-02",
        )
        self.check(
            "VER-405",
            (self.repo / "context" / "reviews" / "REVIEW-PROTOCOL-PROPOSAL.md").is_file()
            and "context/reviews/" in readme,
            "context/reviews/ holds the review artifacts and the README describes the directory (D-024)",
            "review artifacts live in context/reviews/ — never in context/extracted/ or root",
        )

    # ------------------------------------------------------------ C5: one home + scoped consent
    def c5(self) -> None:
        ex = self.read("EXECUTION.md")
        self.check(
            "VER-501",
            bool(ex)
            and "authority order" in ex.lower()
            and "source tiers" in ex.lower()
            and "## 3." in ex,
            "EXECUTION.md exists with the contract map, source tiers, and authority order",
            "EXECUTION.md is the canonical home (D-021)",
        )
        pointers = {}
        for f in ("AGENTS.md", "NORTH-STAR.md", "ENGINEERING.md", "OPERATING-MODEL.md", "PLAN.md"):
            pointers[f] = "EXECUTION.md" in self.read(f)
        self.check(
            "VER-502",
            all(pointers.values()),
            f"all five governing files reference EXECUTION.md ({', '.join(f for f, v in pointers.items() if v)})",
            f"missing pointers: {[f for f, v in pointers.items() if not v]}",
        )
        chain_re = re.compile(r"(LAWS\s*>\s*ENGINEERING|ENGINEERING\s*>\s*PRINCIPLES|Intent Ledger\)\s*>)")
        stray = [f for f in ("NORTH-STAR.md", "ENGINEERING.md", "OPERATING-MODEL.md") if chain_re.search(self.read(f))]
        self.check(
            "VER-503",
            not stray,
            "no embedded authority-order chains remain in NORTH-STAR / ENGINEERING / OPERATING-MODEL (single home)",
            f"stray chains in: {stray} — replace with a pointer to EXECUTION.md §3 (D-021)",
        )
        decisions = self.read("DECISIONS.md")
        plan = self.read("PLAN.md")
        open_ok = (
            "## Open owner decisions" in decisions
            and "**Q1**" in decisions
            and "**Q2**" in decisions
            and "**Q3**" in decisions
            and "Standing open" in plan
            and "## 6" in ex
            and "Q3" in ex
        )
        self.check(
            "VER-504",
            open_ok,
            "Q1/Q2/Q3 remain visibly open in DECISIONS, PLAN, and EXECUTION §6 (with gates and defaults)",
            "open owner decisions must stay visible until their named gates — never closed by interpretation",
        )
        self.check(
            "VER-505",
            "| D-021 " in decisions and "| D-022 " in decisions and "| D-023 " in decisions,
            "D-021/D-022/D-023 recorded (canonical home, source tiers, workflow boundary)",
            "record the canonicalization decisions",
        )
        self.check(
            "VER-506",
            "consent for DEFAULTABLE questions only" in ex,
            "EXECUTION §6: silence-consent is SCOPED to defaultable questions at their lock gates (F-02)",
            "scope the consent rule — blocking questions (owner intent, irreversible, security, data loss) never close by silence or elapsed time",
        )
        om = self.read("OPERATING-MODEL.md")
        self.check(
            "VER-507",
            "INT-070, governing" in om and "recommended where possible" not in om,
            "OPERATING-MODEL §9: GLM-based verification is governing (INT-070); cross-family is optional coverage, never the default (F-03)",
            "make the verifier family rule consistent with INT-070 across DECISIONS/EXECUTION/OPERATING-MODEL",
        )
        d024 = next((ln for ln in decisions.splitlines() if ln.startswith("| D-024 ")), "")
        self.check(
            "VER-508",
            bool(d024) and "change channel" in d024 and "STATE.md" in d024 and "ADOPTED" in d024,
            "D-024 recorded as ADOPTED (change channel + STATE.md + session records + walls stage-1 + self-test)",
            "record D-024 — the review-merge adoption, severable and challengeable",
        )

    # ------------------------------------------------------------ C6: this run is the proof
    def c6(self) -> None:
        self.check(
            "VER-601",
            (self.repo / "tools" / "verify_canonical_layer.py").is_file(),
            "the verifier exists in-repo and this run is the proof (not a written report)",
            "tools/verify_canonical_layer.py must live in the repo (EXECUTION.md §7)",
        )

    # ------------------------------------------------------------ C7: the garden (STATE, FAIL, reviews)
    def c7(self) -> None:
        state = self.read("STATE.md")
        self.check(
            "VER-701",
            bool(state)
            and "NOT authority" in state
            and "- **Phase:**" in state
            and "- **Exact next action:**" in state
            and "**Blocking open questions" in state
            and "**Verification state" in state,
            "STATE.md exists with the required BOLD fields (phase, next action, open questions, verification state) and the not-authority disclaimer",
            "restore /STATE.md with the D-024 fields — a navigation snapshot, never authority; fields must be actual bold list items, not decorative text",
        )
        m = re.search(r"context/extracted/(\d+-[A-Za-z0-9-]+\.md)", state)
        target = f"context/extracted/{m.group(1)}" if m else ""
        self.check(
            "VER-702",
            bool(target) and (self.repo / target).is_file(),
            f"STATE.md's session-record pointer resolves on disk ({target or 'none found'})",
            "STATE.md must point at the latest numbered session record and the file must exist",
        )
        fail = self.read("failures/FAIL-001.yaml")
        self.check(
            "VER-703",
            "id: FAIL-001" in fail
            and "constraint_added:" in fail
            and "known_bad:" in fail
            and "GH-PROTECTION-REJECT" in fail,
            "FAIL-001 recorded: the direct-to-main incident with constraint, known-bad, and expected code (RAT-01/02 executed)",
            "failures/FAIL-001.yaml must exist with class, evidence, constraint, and known-bad proof",
        )
        self.check(
            "VER-704",
            (self.repo / "context" / "reviews" / "REVIEW-PROTOCOL-PROPOSAL.md").is_file()
            and "context/reviews/" in self.read("EXECUTION.md"),
            "the review protocol proposal lives in context/reviews/ and EXECUTION.md names the review-artifact home (D-024)",
            "review artifacts belong in context/reviews/ with the canonical pointer in EXECUTION.md §1",
        )

    # ------------------------------------------------------------ C8: coverage control (manifest, fidelity, immutability, freshness)
    def c8(self) -> None:
        """F-09/D-025: the source-coverage control. Quote fidelity, raw immutability,
        manifest structure, and STATE freshness are CHECKED properties, not prose."""
        manifest = self.read("context/SOURCE-COVERAGE-MANIFEST.md")
        self.check(
            "VER-801",
            bool(manifest)
            and "SOURCE-COVERAGE-MANIFEST" in manifest
            and all(f"`{name}`" in manifest for name in EXPECTED_RAW)
            and "## 2. Non-raw owner-turn provenance" in manifest
            and "## 3. Exception register" in manifest
            and "## 4. Exclusion register" in manifest
            and len(re.findall(r"[0-9a-f]{64}", manifest)) >= len(EXPECTED_RAW),
            f"the source-coverage manifest exists with all {len(EXPECTED_RAW)} raw files classified, INT-mapped, SHA-256-anchored, with provenance/exception/exclusion registers (F-09, D-025)",
            "restore context/SOURCE-COVERAGE-MANIFEST.md per D-025 — every raw file classified and anchored; exceptions and exclusions enumerated, never silent",
        )

        # VER-802: raw immutability (AUT-02 at C3 — was prose-only)
        import hashlib

        mismatches = []
        for name in EXPECTED_RAW:
            p = self.repo / "context" / "raw" / name
            if not p.is_file():
                mismatches.append(f"{name} (missing)")
                continue
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
            if digest not in manifest:
                mismatches.append(name)
        self.check(
            "VER-802",
            not mismatches,
            f"every raw file's SHA-256 matches the manifest anchor — context/raw/ is mechanically immutable ({len(EXPECTED_RAW)} files)",
            f"context/raw/ was edited (mismatched: {', '.join(mismatches)}) — AUT-02 forbids raw edits; restore the file from git history and record intent through the ledger instead",
        )

        # VER-803: quote fidelity — every raw-cited ledger quote validates against its source
        ledger = self.read("INTENT-LEDGER.md")
        entries = [e for e in re.split(r"(?=^\*\*INT-\d+)", ledger, flags=re.M) if re.match(r"^\*\*INT-\d+", e)]
        fidelity_failures: list[str] = []
        for entry in entries:
            # an entry ends at the first section boundary (--- or ## header) — audit notes
            # and section commentary after the boundary are NOT part of the entry
            entry = re.split(r"^---\s*$|^## ", entry, maxsplit=1, flags=re.M)[0]
            iid = re.match(r"^\*\*(INT-\d+)", entry).group(1)
            src_m = re.search(r"^Source: (.+)$", entry, flags=re.M)
            if not src_m:
                fidelity_failures.append(f"{iid}: no Source line (the INT-035 defect class)")
                continue
            source_text = src_m.group(1)
            # raw citations = backtick spans naming context/raw files (txt or md) with
            # line refs — parsed into PER-CITATION windows (sub-agent finding 7b: a quote
            # must appear in the cited REGION, not merely somewhere in the cited file)
            citations: list[tuple[str, int, int]] = []
            for span in re.findall(r"`([^`]+)`", entry):
                for m in re.finditer(r"(?:context/raw/)?([\w .\-]+\.(?:txt|md)):\s*([\d\u2013\-/,\s;]+)", span):
                    fname = m.group(1)
                    if fname not in EXPECTED_RAW:
                        continue
                    for piece in re.finditer(r"(\d+)(?:\s*[\u2013\-]\s*(\d+))?", m.group(2)):
                        a = int(piece.group(1))
                        b = int(piece.group(2) or piece.group(1))
                        citations.append((fname, a, max(a, b)))
            raw_files = sorted(set(f for f, _, _ in citations))
            # quotes: block-quote lines — extract each "..." span (a line may carry inline
            # citations between spans, e.g. INT-081: `> "quote" (`0.txt:1323`) · "quote2"`)
            quotes: list[str] = []
            for ln in entry.splitlines():
                if ln.startswith("> ") or ln.startswith(">"):
                    quotes.extend(re.findall(r'"([^"]+)"', ln))
            if raw_files:
                file_cache: dict[str, list[str]] = {
                    f: (self.repo / "context" / "raw" / f).read_text(encoding="utf-8", errors="replace").splitlines()
                    for f in raw_files
                }
                for q in quotes:
                    for frag in _fragments(q):
                        if len(frag) < 20:
                            continue
                        found = any(
                            frag
                            in _normalize_for_fidelity(
                                "\n".join(
                                    file_cache[fname][max(0, a - 11): min(len(file_cache[fname]), b + 20)]
                                )
                            )
                            for fname, a, b in citations
                        )
                        if not found:
                            fidelity_failures.append(
                                f"{iid}: quote fragment not found in any cited source WINDOW (cited: {', '.join(sorted(set(f'{f}:{a}' for f, a, _ in citations)))}) — wrong file, wrong region, or fabricated"
                            )
                            break
            else:
                # non-raw source: must name a durable home (session record / chat turn / extracted path)
                if not re.search(r"session record|owner turn|chat|06-REASONING-LOG|context/extracted/", source_text):
                    fidelity_failures.append(f"{iid}: Source names no raw file and no durable home (E-2 discipline)")
        self.check(
            "VER-803",
            not fidelity_failures,
            f"every ledger entry carries a Source line; every raw-cited quote validates mechanically against its source ({len(entries)} entries checked; exceptions E-1/E-5/E-6 normalized per the manifest)",
            f"quote-fidelity failures: {'; '.join(fidelity_failures[:6])} — repair per SOURCE-COVERAGE-MANIFEST §3/§6 (fabrication and transcription drift are caught here, never trusted)",
        )

        # VER-804: STATE freshness — the pointer must reference the highest-numbered session record
        state = self.read("STATE.md")
        records = sorted(
            (int(m.group(1)) for m in (re.match(r"^(\d+)-", p.name) for p in (self.repo / "context" / "extracted").glob("*.md") if m)),
        )
        highest = records[-1] if records else -1
        state_refs = [int(m.group(1)) for m in re.finditer(r"context/extracted/(\d+)-", state)]
        self.check(
            "VER-804",
            bool(state_refs) and max(state_refs) == highest,
            f"STATE.md's session-record pointer ({max(state_refs) if state_refs else 'none'}) equals the highest-numbered record on disk ({highest}) — staleness is caught, not remembered",
            "update /STATE.md at session exit to point at the newest numbered session record (AGENTS.md session-exit rule; a stale STATE.md is a drift finding)",
        )

    def run(self) -> list[tuple[str, bool, str]]:
        for fn in (self.c1, self.c2, self.c3, self.c4, self.c5, self.c6, self.c7, self.c8):
            fn()
        return self.results


# ---------------------------------------------------------------- self-test (KB discipline)
# Each mutation breaks ONE protected property on a temp copy; the named check MUST fail.

MUTATIONS: list[tuple[str, str, callable, str]] = [
    (
        "MUT-14",
        "tamper a raw corpus file (append whitespace to 0.txt) — AUT-02 was prose-only before the manifest",
        lambda r: _edit(r, "context/raw/0.txt", "\\n", "\\n "),
        "VER-802",
    ),
    (
        "MUT-15",
        "fabricate a ledger quote (mutate INT-083's words into text that is not in raw)",
        lambda r: _edit(
            r,
            "INTENT-LEDGER.md",
            "1 - smallest daily loop. i read books, i import articles, posts, writings, research paper, pdfs, md's and any thing readable.",
            "1 - biggest quarterly waterfall. i sail boats, i export articles, posts, writings, research paper, pdfs, md's and any thing readable.",
        ),
        "VER-803",
    ),
    (
        "MUT-16",
        "delete the source-coverage manifest — the coverage control disappears",
        lambda r: _rm(r, "context/SOURCE-COVERAGE-MANIFEST.md"),
        "VER-801",
    ),
    (
        "MUT-17",
        "stale STATE pointer — rewrite the highest session-record reference in STATE.md to a lower record on disk",
        lambda r: _stale_state_pointer(r),
        "VER-804",
    ),
    (
        "MUT-18",
        "strip a restored Source line from INT-035 — the no-provenance defect class returns",
        lambda r: _edit(
            r,
            "INTENT-LEDGER.md",
            "Source: `context/raw/3.txt:5` (Source line restored 2026-10-14 — was missing; located by search, quote matches verbatim; see `context/SOURCE-COVERAGE-MANIFEST.md` §6). Grounds: P-15, OPERATING-MODEL §3 (the commit protocol), FAIL-002.",
            "",
        ),
        "VER-803",
    ),
    (
        "MUT-19",
        "add a banner-less file to context/extracted/ — the static-BRIEFS blind spot the sub-agent found (F-01 class recurring in the verifier)",
        lambda r: (r / "context" / "extracted" / "13-TEST-NO-BANNER.md").write_text("no status banner here\n", encoding="utf-8"),
        "VER-205",
    ),
    (
        "MUT-20",
        "wrong-line citation: point INT-083 at 1.txt:100 while its quote lives at 1.txt:444 — the file-level-vs-region gap the sub-agent found",
        lambda r: _edit(r, "INTENT-LEDGER.md", "Source: `context/raw/1.txt:444` (answer to the day-30 daily-loop question). Grounds: D-013, D-023, PLAN Phase 4 exit, INT-019.", "Source: `context/raw/1.txt:100` (answer to the day-30 daily-loop question). Grounds: D-013, D-023, PLAN Phase 4 exit, INT-019."),
        "VER-803",
    ),
    (
        "MUT-01",
        "remove the newest ledger entry (INT-091) — the F-01 class: entries vanish past a frozen bound",
        lambda r: _edit(r, "INTENT-LEDGER.md", "**INT-091 — REVIEW-THE-REVIEWS AND MERGE — active**\n", ""),
        "VER-212",
    ),
    (
        "MUT-02",
        "duplicate a ledger header (INT-091 twice) — uniqueness must catch it",
        lambda r: _edit(
            r,
            "INTENT-LEDGER.md",
            "**INT-091 — REVIEW-THE-REVIEWS AND MERGE — active**",
            "**INT-091 — REVIEW-THE-REVIEWS AND MERGE — active**\n**INT-091 — DUPLICATE — active**",
        ),
        "VER-201",
    ),
    (
        "MUT-03",
        "corrupt a status ('active' → 'actve') — the old regex was blind to bad statuses",
        lambda r: _edit(r, "INTENT-LEDGER.md", "REVIEW-THE-REVIEWS AND MERGE — active", "REVIEW-THE-REVIEWS AND MERGE — actve"),
        "VER-202",
    ),
    (
        "MUT-04",
        "delete /STATE.md — the current-state index disappears",
        lambda r: _rm(r, "STATE.md"),
        "VER-701",
    ),
    (
        "MUT-05",
        "remove the GLM verification rule from AGENTS.md (INT-070)",
        lambda r: _edit(r, "AGENTS.md", "- Test and verification loops run on GLM-based subagents; GLM is the host agent for verification/testing (INT-070).\n", ""),
        "VER-109",
    ),
    (
        "MUT-06",
        "restore the blanket 'silence is consent' (F-02 regression)",
        lambda r: _edit(r, "EXECUTION.md", "silence past a named gate is consent for DEFAULTABLE questions only (QST-03)", "silence past a named gate is consent (QST-03)"),
        "VER-506",
    ),
    (
        "MUT-07",
        "remove the change-channel rule from AGENTS.md (FAIL-001's guard)",
        lambda r: _edit(
            r,
            "AGENTS.md",
            "- **Change channel (D-024): findings are recorded; changes are applied only through reviewed branches.** Analysis, review, and proposal artifacts NEVER land on `main` directly — they arrive on a branch, through a pull request, and merge only with the owner's explicit authorization. Memory deltas (owner words, decisions, ledgers, worklog, plan, session records) land per P-15: branch + PR + merge under the standing authorization of P-13/P-15 (the owner reviews at gates, not per-merge). With walls stage-1 live, direct pushes to `main` are rejected by the host.\n",
            "",
        ),
        "VER-107",
    ),
    (
        "MUT-08",
        "drop INTENT-LEDGER.md from read-order step 1 (boot-sequence regression)",
        lambda r: _edit(r, "AGENTS.md", "1. `/INTENT-LEDGER.md` — owner words, verbatim, statused. The highest authority. Load it BEFORE forming any understanding of the task.", "1. `/GLOSSARY.md` — vocabulary"),
        "VER-101",
    ),
    (
        "MUT-09",
        "break INT-051's superseded_by link (silent supersession)",
        lambda r: _edit(r, "INTENT-LEDGER.md", "superseded (superseded_by: INT-030)", "superseded"),
        "VER-204",
    ),
    (
        "MUT-10",
        "delete failures/FAIL-001.yaml — a failure loses its record",
        lambda r: _rm(r, "failures/FAIL-001.yaml"),
        "VER-703",
    ),
    (
        "MUT-11",
        "remove the F-05 qualifier — tags become a gate for concept formation again",
        lambda r: _edit(r, "NORTH-STAR.md", "Concept formation (C4) reads owner-authored tags as ONE signal, never a gate:", "Concept formation (C4) reads owner-authored tags."),
        "VER-211",
    ),
    (
        "MUT-12",
        "delete the review protocol proposal — review artifacts lose their home",
        lambda r: _rm(r, "context/reviews/REVIEW-PROTOCOL-PROPOSAL.md"),
        "VER-704",
    ),
    (
        "MUT-13",
        "gut STATE.md's required fields (keep the file, lose the index)",
        lambda r: _edit(r, "STATE.md", "- **Exact next action:**", "- ~~Exact next action:~~"),
        "VER-701",
    ),
]


def _edit(repo: Path, rel: str, old: str, new: str) -> None:
    p = repo / rel
    p.write_text(p.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")


def _rm(repo: Path, rel: str) -> None:
    (repo / rel).unlink()


def _stale_state_pointer(repo: Path) -> None:
    """MUT-17, content-generic (repaired 2026-10-14): rewrite STATE.md's highest
    session-record reference to the highest LOWER-numbered record that exists on
    disk. The earlier hard-coded pointer (12-GAP-CLOSURE...) would silently no-op
    the moment STATE advanced to record 13 — the mutation would not apply, VER-804
    would not fail, and the self-test would report a blind guard, RED-blocking the
    very PRs that legitimately advance the record sequence. Generic form: works on
    every future tree, exercises exactly the stale-pointer failure class."""
    state = repo / "STATE.md"
    text = state.read_text(encoding="utf-8")
    refs = sorted(
        (int(m.group(1)), m.group(0))
        for m in re.finditer(r"context/extracted/(\d+)-[\w.\-]+\.md", text)
    )
    if not refs:
        return
    hi_num, hi_ref = refs[-1]
    lower = [
        p
        for p in (repo / "context" / "extracted").glob("*.md")
        if (m := re.match(r"^(\d+)-", p.name)) and int(m.group(1)) < hi_num
    ]
    if not lower:
        return
    lo = max(lower, key=lambda p: int(re.match(r"^(\d+)-", p.name).group(1)))
    state.write_text(
        text.replace(hi_ref, f"context/extracted/{lo.name}"), encoding="utf-8"
    )


def _normalize_for_fidelity(text: str) -> str:
    """VER-803 normalization (manifest exceptions E-5/E-6): whitespace collapsed,
    quote characters (straight and curly, single and double) removed SYMMETRICALLY
    from both the corpus and the fragment, em/en dashes unified, and whitespace
    before punctuation collapsed (the INT-057 cosmetic class). Symmetric removal
    keeps fidelity: a fabricated quote still cannot match text that does not exist."""
    text = text.replace("\u201c", '"').replace("\u201d", '"').replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u2014", "-").replace("\u2013", "-").replace("\u2026", "...")
    text = text.replace('"', "").replace("'", "")
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return re.sub(r"\s+", " ", text)


def _fragments(quote_line: str) -> list[str]:
    """Split a ledger quote into validation fragments: strip the outer quote marks,
    remove bracketed editorial glosses (E-6: '[answering: ...]'), split on ellipsis
    (E-1: elided excerpts), normalize and STRIP each fragment (the INT-060 class:
    a spaced ellipsis 'done ... and' leaves trailing whitespace the corpus's
    punctuation normalization collapses)."""
    q = quote_line.strip().strip('"').strip()
    q = re.sub(r"\[[^\]]*\]", " ", q)  # E-6: editorial brackets are not owner text
    parts = re.split(r"\.\.\.|\u2026", q)  # E-1: elisions produce fragments
    return [_normalize_for_fidelity(p).strip() for p in parts if p.strip()]


def self_test(repo: Path) -> int:
    caught, missed = [], []
    print(f"known-bad self-test — {len(MUTATIONS)} mutations, each must FAIL its named check\n")
    for code, desc, mutate, expect in MUTATIONS:
        with tempfile.TemporaryDirectory(prefix="arivoo-kb-") as td:
            copy = Path(td) / "repo"
            shutil.copytree(repo, copy, ignore=shutil.ignore_patterns(".git"))
            mutate(copy)
            layer = Layer(copy)
            try:
                layer.run()
            except Exception as exc:  # a crashed checker is a caught guard
                caught.append((code, expect, f"crash: {exc}"))
                print(f"{code} PASS  {desc} → checker raised: {exc}")
                continue
            ok = layer.failed(expect)
            if ok:
                caught.append((code, expect, ""))
                print(f"{code} PASS  {desc} → {expect} FAILed as required")
            else:
                missed.append((code, expect))
                print(f"{code} FAIL  {desc} → {expect} did NOT fail — the guard is blind (KB-05)")
    print()
    if missed:
        print(f"SELF-TEST RED — {len(missed)} blind guard(s): {[c for c, _ in missed]}")
        print("A green checker with untested blind spots gives agents unjustified confidence (F-01).")
        return 1
    print(f"SELF-TEST GREEN — {len(caught)}/{len(MUTATIONS)} known-bad mutations caught by their named checks.")
    print("The guards are themselves tested (KB-01..06 spirit, document-level).")
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        return self_test(REPO)

    layer = Layer(REPO)
    results = layer.run()
    failures = [(c, w) for c, ok, w in results if not ok]
    print(f"canonicalization-layer verifier — {len(results)} checks, {len(failures)} failures")
    print(f"repo: {REPO}")
    print()
    for code, ok, what in results:
        mark = "PASS" if ok else "FAIL"
        print(f"{code} {mark}  {what}")
    if failures:
        print()
        print("RED — the canonicalization conditions do not hold. Repair per the FIX lines above.")
        print("Ref: /EXECUTION.md §7, INT-068 acceptance conditions, D-024 drift gates.")
        return 1
    print()
    print("GREEN — the canonicalization conditions hold on the real repository files:")
    print("  C1 boot: Ledger first + STATE.md step 2  C2 traceability: dynamic ledger range + statuses + banners")
    print("  C3 D-004/D-015/P-16 reconciled  C4 archive historical, raw mixed, reviews re-homed")
    print("  C5 one home; consent scoped; GLM governing; D-024  C6 proven by this run")
    print("  C7 garden: STATE live, FAIL-001 + known-bad, review artifacts in context/reviews/")
    print("  C8 coverage: manifest + raw immutability + quote fidelity + STATE freshness (F-09/D-025)")
    print("Run with --self-test to prove the guards catch the failure classes (F-01).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
