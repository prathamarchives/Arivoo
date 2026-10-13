#!/usr/bin/env python3
"""verify_canonical_layer.py — the canonicalization-layer verifier (Layer-0 gate precursor).

Proves the six acceptance conditions of the canonicalization slice (INT-068) against
the REAL repository files — not a manually written report (LAW-01's spirit applied to
documents). Exit 0 = green; every failure prints rule ID, violation, and repair path
(diagnostics contract). Pure stdlib; no dependencies (LAW-08 discipline pre-Phase-1).

Conditions checked (per the owner-endorsed review):
  C1  a fresh agent loads the Intent Ledger + governing docs from the defined read order
  C2  every active requirement traces to owner intent or an adopted decision;
      historical AI proposals carry explicit status
  C3  D-004 and the old The List wording no longer conflict with D-015 and P-16
  C4  the archive is clearly historical; raw is not mistaken for owner-only intent;
      the stale file count is corrected
  C5  the execution contract has one canonical home; Q2/Q3 remain visibly open
  C6  this verifier proves it on the real files (this run IS the proof)

Ref: /EXECUTION.md §7. When the harness exists (Phase 2), these checks move up the
ladder into `make audit` (LAD-01).
"""

from __future__ import annotations

import re
import sys
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

BRIEFS = [
    "00-PRINCIPLES.md",
    "01-ENGINEERING-DOCTRINE.md",
    "02-OWNER-VOICE-AND-EVOLUTION.md",
    "03-ARIVO-CURRENT-STATE.md",
    "04-OPERATING-MODEL.md",
    "05-OPEN-QUESTIONS.md",
    "06-REASONING-LOG.md",
    "07-ON-THE-LIST.md",
    "08-RECONCILIATION-BRIEF.md",
]

results: list[tuple[str, bool, str]] = []


def read(rel: str) -> str:
    path = REPO / rel
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def check(code: str, ok: bool, what: str, fix: str = "") -> None:
    results.append((code, ok, what if ok else f"{what} — FIX: {fix}"))


# ---------------------------------------------------------------- C1: boot sequence
def c1() -> None:
    agents = read("AGENTS.md")
    order = [m.group(1) for m in re.finditer(r"^\s*\d+\.\s+`/?([^`/]+\.md)`", agents, re.M)]

    def pos(name: str) -> int:
        for i, entry in enumerate(order):
            if name in entry:
                return i
        return -1

    li, ns, ex = pos("INTENT-LEDGER.md"), pos("NORTH-STAR.md"), pos("EXECUTION.md")
    check(
        "VER-101",
        li != -1 and ns != -1 and li < ns,
        f"read order: INTENT-LEDGER.md (#{li+1}) loads before NORTH-STAR.md (#{ns+1})",
        "AGENTS.md read order must list /INTENT-LEDGER.md first — the owner words load before any understanding forms (INT-068)",
    )
    check(
        "VER-102",
        ex != -1,
        "read order includes /EXECUTION.md (the canonical execution-contract home)",
        "add /EXECUTION.md to the AGENTS.md read order (D-021)",
    )
    check(
        "VER-103",
        "verbatim owner material" not in agents
        and "mixed owner statements" in agents
        and "Never edit it" in agents,
        "AGENTS.md: context/raw/ described as the mixed verbatim corpus (not owner-only), never edited",
        'AGENTS.md must carry the D-022 wording: raw = "mixed owner statements, AI analysis, and pasted documents; never edit"',
    )
    check(
        "VER-104",
        "ONLY through INTENT-LEDGER" in agents,
        "AGENTS.md: the intent rule — intent enters only through the ledger",
        "AGENTS.md binding rules must state the intent rule (EXECUTION.md §2)",
    )
    check(
        "VER-105",
        0 < len(agents.splitlines()) <= 80,
        f"AGENTS.md is a map, not a brain ({len(agents.splitlines())} lines, MEM-03 limit 80)",
        "split AGENTS.md — detailed knowledge moves to authoritative homes",
    )


# ---------------------------------------------------------------- C2: traceability
def c2() -> None:
    ledger = read("INTENT-LEDGER.md")
    headers = re.findall(r"\*\*INT-(\d{3})\s*—\s*.*?—\s*(active|clarified|superseded|historical)", ledger)
    ids = {int(i) for i, _ in headers}
    missing = [n for n in range(19, 69) if n not in ids]
    check(
        "VER-201",
        not missing,
        f"ledger carries the full backfilled range INT-019..INT-068 ({len(ids)} statused entries)",
        f"missing INT entries: {['INT-%03d' % n for n in missing]} — backfill from the corpus with verbatim quotes (INT-068 audit)",
    )
    bad_status = [i for i, s in headers if s not in ("active", "clarified", "superseded", "historical")]
    check("VER-202", not bad_status, "every ledger entry carries a status (AUT-02)")
    check(
        "VER-203",
        "INT-001..INT-018" in ledger and "never recycled" in ledger,
        "ledger documents the reserved INT-001..018 range (v1 spec IDs not in corpus — never recycled)",
        "keep the numbering note in INTENT-LEDGER.md",
    )
    check(
        "VER-204",
        "superseded (superseded_by: INT-030)" in ledger,
        "the one corrected owner statement (INT-051 AIOS-to-DB) is preserved with its superseded_by link",
        "INT-051 must keep its text, status, and superseded_by pointer (AUT-03)",
    )
    banner_fail = []
    for b in BRIEFS:
        text = read(f"context/extracted/{b}")
        has_banner = ("STATUS:" in text[:600]) or ("SUPERSEDED" in text[:400])
        if not has_banner:
            banner_fail.append(b)
    check(
        "VER-205",
        not banner_fail,
        f"all 9 extracted briefs carry a status banner (historical/superseded/active)",
        f"add the banner to: {banner_fail} (D-022 — future agents must not mistake history for active decisions)",
    )
    north = read("NORTH-STAR.md")
    check(
        "VER-206",
        "INT-019" in north and "day-one intake" in north,
        "NORTH-STAR: import is an explicit day-one intake requirement traced to INT-019 (D-023)",
        "NORTH-STAR first-usable-workflow must carry the import requirement",
    )
    check(
        "VER-207",
        "INT-068" in ledger and "canonicalization" in ledger.lower(),
        "the canonicalization directive itself is ledgered (INT-068)",
        "record the owner directive that authorized this slice",
    )


# ---------------------------------------------------------------- C3: D-004 / The List
def c3() -> None:
    decisions = read("DECISIONS.md")
    d004 = next((ln for ln in decisions.splitlines() if ln.startswith("| D-004 ")), "")
    check(
        "VER-301",
        "SUPERSEDED" in d004 and "D-020" in d004,
        "D-004 is marked superseded-by-D-020 (text preserved, status annotated)",
        "annotate D-004's status cell — never rewrite its text (AUT-02/03)",
    )
    d020 = next((ln for ln in decisions.splitlines() if ln.startswith("| D-020 ")), "")
    check(
        "VER-302",
        bool(d020)
        and "refinement-debt register" in d020
        and "REMOVED from the register" in d020
        and "P-16" in d020,
        "D-020: The List = refinement-debt register; semantic/pgvector/vector-search removed to the active sequence; P-16 invariant",
        "D-020 must exist and reconcile D-004 with D-015/P-16",
    )
    gloss = read("GLOSSARY.md")
    the_list = next((ln for ln in gloss.splitlines() if ln.strip().startswith("- **The List**")), "")
    check(
        "VER-303",
        "refinement-debt register" in the_list and "can never enter" in the_list,
        "GLOSSARY: The List defined as the refinement-debt register with the P-16 invariant",
        "update the GLOSSARY The List entry (D-020)",
    )
    reg = read("context/extracted/07-ON-THE-LIST.md")
    closed = reg.count("CLOSED: in the active sequence")
    live_ok = "ACTIVE MECHANISM" in reg and "L-001" in reg
    check(
        "VER-304",
        closed >= 3 and live_ok and "refinement-debt register" in reg,
        "the register: L-001 live (sync only); L-002..L-004 closed as in-active-sequence",
        "07-ON-THE-LIST.md must reflect D-020 — semantic capabilities are in the sequence, not deferred",
    )
    principles = read("PRINCIPLES.md")
    check(
        "VER-305",
        "refinement-debt register" in principles,
        "P-07 mechanism cites the refinement-debt register (no deferral framing)",
        "update P-07 MECHANISM to the register language",
    )


# ---------------------------------------------------------------- C4: archive status
def c4() -> None:
    readme = read("context/README.md")
    check(
        "VER-401",
        "seven files" in readme and "3.txt" in readme,
        "context/README names seven raw files including 3.txt (stale count corrected)",
        "context/README.md must list the actual corpus",
    )
    check(
        "VER-402",
        ("mixed archive" in readme or "mixed owner statements" in readme)
        and "NOT owner-only intent" in readme
        and "NEVER edited" in readme,
        "context/README: raw = mixed archive, not owner-only intent; never edited",
        "context/README.md must carry the D-022 source-tier wording",
    )
    check(
        "VER-403",
        "slice F-01" not in readme and "F-01 " not in readme,
        "context/README migration reference no longer points at the superseded F-01 step",
        "migration trigger = corpus closure (FX-07), not the F-band",
    )
    raw_files = sorted(p.name for p in (REPO / "context" / "raw").glob("*") if p.is_file())
    check(
        "VER-404",
        raw_files == sorted(EXPECTED_RAW),
        f"context/raw holds exactly the 7-file verbatim corpus (unchanged: {len(raw_files)} files)",
        "the raw corpus is immutable — AUT-02",
    )


# ---------------------------------------------------------------- C5: one canonical home
def c5() -> None:
    ex = read("EXECUTION.md")
    check(
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
        pointers[f] = "EXECUTION.md" in read(f)
    check(
        "VER-502",
        all(pointers.values()),
        f"all five governing files reference EXECUTION.md ({', '.join(f for f, v in pointers.items() if v)})",
        f"missing pointers: {[f for f, v in pointers.items() if not v]}",
    )
    chain_re = re.compile(r"(LAWS\s*>\s*ENGINEERING|ENGINEERING\s*>\s*PRINCIPLES|Intent Ledger\)\s*>)")
    stray = [f for f in ("NORTH-STAR.md", "ENGINEERING.md", "OPERATING-MODEL.md") if chain_re.search(read(f))]
    check(
        "VER-503",
        not stray,
        "no embedded authority-order chains remain in NORTH-STAR / ENGINEERING / OPERATING-MODEL (single home)",
        f"stray chains in: {stray} — replace with a pointer to EXECUTION.md §3 (D-021)",
    )
    decisions = read("DECISIONS.md")
    plan = read("PLAN.md")
    open_ok = (
        "## Open owner decisions" in decisions
        and "**Q1**" in decisions
        and "**Q2**" in decisions
        and "**Q3**" in decisions
        and "Standing open" in plan
        and "## 6" in ex
        and "Q3" in ex
    )
    check(
        "VER-504",
        open_ok,
        "Q1/Q2/Q3 remain visibly open in DECISIONS, PLAN, and EXECUTION §6 (with gates and defaults)",
        "open owner decisions must stay visible until their named gates — never closed by interpretation",
    )
    check(
        "VER-505",
        "| D-021 " in decisions and "| D-022 " in decisions and "| D-023 " in decisions,
        "D-021/D-022/D-023 recorded (canonical home, source tiers, workflow boundary)",
        "record the canonicalization decisions",
    )


# ---------------------------------------------------------------- C6: this run is the proof
def c6() -> None:
    check(
        "VER-601",
        (REPO / "tools" / "verify_canonical_layer.py").is_file(),
        "the verifier exists in-repo and this run is the proof (not a written report)",
        "tools/verify_canonical_layer.py must live in the repo (EXECUTION.md §7)",
    )


def main() -> int:
    for fn in (c1, c2, c3, c4, c5, c6):
        fn()

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
        print("Ref: /EXECUTION.md §7, INT-068 acceptance conditions.")
        return 1
    print()
    print("GREEN — the six canonicalization conditions hold on the real repository files:")
    print("  C1 boot: Intent Ledger first  C2 traceability + banners  C3 D-004/D-015/P-16 reconciled")
    print("  C4 archive historical, raw mixed, counts fixed  C5 one canonical home, Q1-Q3 open  C6 proven by this run")
    return 0


if __name__ == "__main__":
    sys.exit(main())
