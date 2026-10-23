#!/usr/bin/env python3
"""verify_selftest.py — the H-01b trusted candidate-tool execution floor (A03).

The base-owned mutation suite: 35 known-bad corpus mutations, each of which the
CANDIDATE's verify_canonical_layer.py must catch with its named check. This
module is anchored from main by CI (D-035: the coordinated-weakening floor) and
judges whichever candidate tree it is pointed at.

H-01b (owner turns 21/22, INT-126/INT-127, D-040/D-041; PLAN card; the
CodeRabbit F-005/F-013 routing) rebuilt the trust boundary. The predecessor
imported the candidate verifier IN-PROCESS (line 30 of the old file) — a
`SystemExit(0)` at candidate import exited the whole suite green with zero
output (the A03 vacuous pass, reproduced in record 21 §4), a checker exception
counted as a "caught guard", and the candidate controlled the corpus path. THIS
driver:

1. never imports candidate code into its own interpreter — stdlib only, no
   sys.path sibling imports (the machinery lives in tools/mutation_runner.py,
   loaded BY PATH — the gate.py importlib-spec precedent — so `python3 -I`
   keeps the candidate's tools/ from shadowing anything, F-005);
2. runs every mutation case in a FRESH DISPOSABLE child process over a bounded
   fixture: regular files only (symlinks/devices/fifos/sockets refused — never
   dereferenced, F-013/F-002), per-file/total/count budgets, race-resistant
   O_NOFOLLOW reads, cleanup established before any construction;
3. re-verifies integrity BEFORE EVERY CASE: the anchored driver's own digest
   against the trusted base copy (when --floor-base / ARV_FLOOR_BASE_TOOLS is
   set) and the corpus source digest against the run's baseline — a mid-run
   source mutation is a named refusal (ARV-FLOOR-002), never a silent judgment
   of changed input;
4. accepts a case ONLY on the full per-case protocol: nonzero exit + the
   expected code's `FAIL` line + the verifier's completion count-line + no
   traceback. Exit-0, printed-words-without-refusal, crashes, timeouts, floods
   and missing verifiers are named refusals (ARV-FLOOR-001/003/005) — never
   catches;
5. writes a completion MANIFEST bound to this run (driver/candidate/corpus
   digests, every expected case exactly once with its actual outcome) and
   validates it (ARV-FLOOR-006) before any GREEN.

Named codes (frozen in harness/tests/test_mutation_floor.py BEFORE this code):
  ARV-FLOOR-001  an expected case was NOT caught (vacuous/absent/incomplete)
  ARV-FLOOR-002  integrity failure (anchor/digest/mid-run corpus change)
  ARV-FLOOR-003  an invalid catch form (traceback / timeout / flood)
  ARV-FLOOR-004  fixture refusal (non-regular entry / budget / count)
  ARV-FLOOR-005  the candidate verifier is missing (fail-closed)

Usage:  python3 tools/verify_selftest.py [--repo DIR] [--only MUT-04[,...]]
        [--floor-base DIR] [--manifest-out PATH] [--case-timeout SECONDS]
        [--validate-manifest PATH]
(The --self-test flag of verify_canonical_layer.py delegates here for backward
compatibility; the corpus root is computed from THIS file's location — a caller
argument is never the authority.)

RESIDUAL BOUNDARY (stated, never claimed away): the child runs on the same host
with the same OS user as this driver. That is NOT OS-level sandboxing: a hostile
child could in principle signal or kill the driver — which makes the run RED
(a killed judge writes no manifest and the required check fails), never green —
and the workflow-definition trust boundary is the H-01b-CI card's item. Q10
(token/workflow-tamper hardening) remains owner-gated. What this floor DOES
claim: no candidate code ran in this interpreter, every case ran in a fresh
disposable fixture, integrity was re-verified before every case, and the
manifest records what actually happened.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat as statmod
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

# Base-owned constants. H-01b: NO import from verify_canonical_layer — the
# candidate module is executed as a CHILD PROCESS over a disposable fixture,
# never imported here (the reproduced A03 hole was exactly that import).
REPO = Path(__file__).resolve().parent.parent

# The entry-header pattern the MUT-23 mutation needs. This is the BASE's copy
# (kept in deliberate lockstep with the verifier's own pattern; if the verifier
# legitimately changes its header syntax, this copy changes in the same slice).
INT_HEADER = re.compile(r"^\*\*INT-(\d{3})\s+—\s+(.*?)\s+—\s+(.*?)\*\*\s*$", re.M)

# ------------------------------------------------------------------ budgets
PER_FILE_BUDGET = 8 * 1024 * 1024     # per corpus file
TOTAL_BUDGET = 192 * 1024 * 1024      # whole corpus
COUNT_BUDGET = 5000                   # whole corpus
READ_CAP = 1024 * 1024                # child stdout/stderr read-back cap
CHILD_FSIZE = 8 * 1024 * 1024         # child per-file write cap (RLIMIT_FSIZE)
CHILD_AS = 512 * 1024 * 1024          # child address-space cap (RLIMIT_AS)
DEFAULT_CASE_TIMEOUT = 120            # seconds, per case (wall clock)
SKIP_DIRS = {".git", "__pycache__", ".pg"}  # .pg: the gitignored local rig dir — never corpus

POSIX = os.name == "posix"

BOUNDARY = (
    "residual boundary: child processes run on the same host with the same OS user as "
    "this driver — NOT OS-level sandboxing; a hostile child could in principle kill the "
    "judge (the run turns RED, never green); the workflow-definition trust boundary is "
    "H-01b-CI's item; Q10 remains owner-gated. Claims made: no candidate code ran in "
    "this interpreter; every case ran in a fresh disposable fixture; integrity was "
    "re-verified before every case; the manifest records what actually happened."
)

COMPLETION_RE = re.compile(
    r"canonicalization-layer verifier\s+[—-]\s+\d+\s+checks?,\s+\d+\s+failures?", re.I
)


class FloorRefusal(Exception):
    """A named, sanitized refusal. The message NEVER carries a corpus path
    (F-012 class: secret-shaped filenames must not leak into diagnostics)."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# ---------------------------------------------------------------- self-test (KB discipline)
# Each mutation breaks ONE protected property on a disposable fixture; the named
# check MUST fail IN THE CHILD (the candidate verifier over the mutated corpus).

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
        "remove the verification-protocol rule from AGENTS.md — content-generic since 2026-10-14 (session 16 / D-034): removes whichever line(s) carry INT-070, so the mutation cannot no-op when the host wording legitimately changes (the base-anchored self-test RED-flags a no-op as a blind guard — the PR #6/#12/#17 re-target class)",
        lambda r: _drop_verification_rule(r),
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
        "drop the INTENT-LEDGER.md step from the read order (boot-sequence regression) — content-generic since 2026-10-14: removes whichever numbered read-order line names the ledger, so the mutation cannot silently no-op when the boot order changes (the base-anchored self-test RED-flags a no-op as a blind guard)",
        lambda r: _drop_ledger_step(r),
        "VER-101",
    ),
    (
        "MUT-21",
        "regress AGENTS to blanket ledger-first boot — rewrite the numbered INTENT-LEDGER read-order step into the pre-supersession form, whatever its current wording (the INT-107/D-027(3) supersession silently undone)",
        lambda r: _blanket_ledger_boot(r),
        "VER-110",
    ),
    (
        "MUT-22",
        "drop the worklog tail from the boot path — the early coordination step disappears (the INT-107 read path broken)",
        lambda r: _drop_read_order_step(r, "context/WORKLOG.md"),
        "VER-110",
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
        "regress the F-05 qualifier — classification words become a gate for concept formation again (content-generic: targets the 'never a gate' qualifier, whatever the surrounding wording)",
        lambda r: _tag_gate_regression(r),
        "VER-211",
    ),
    (
        "MUT-23",
        "malform the newest entry header (strip its status segment) — the entry vanishes from the strict status view while the entry splitter still sees it",
        lambda r: _malform_header(r),
        "VER-903",
    ),
    (
        "MUT-24",
        "cite a non-existent ledger entry and a non-existent decision in a root document — dangling authority references",
        lambda r: _dangling_ref(r),
        "VER-901",
    ),
    (
        "MUT-25",
        "drift the stated statused-intent count (content-generic: adjusts whatever count AGENTS.md currently states)",
        lambda r: _count_drift(r),
        "VER-902",
    ),
    (
        "MUT-26",
        "silently drop an EXECUTION §6 open-question row — the register disagrees across its mirrors (a closure by prose removal, never by a D-row)",
        lambda r: _open_set_drift(r),
        "VER-504",
    ),
    (
        "MUT-27",
        "reintroduce the superseded tag rule — rewrite NORTH-STAR's 'no tag field' into the optional-tag form while the C4 marker stays (slice 9's class (d), sub-agent finding 1: the P1 blind guard this mutation proved)",
        lambda r: _reintroduce_superseded_rule(r),
        "VER-904",
    ),
    (
        "MUT-28",
        "strip a closed question's closure pointer — D-007's Q1-closure annotation loses its D-028 reference, so the closed question reads as OPEN again in a current canonical document (the Arivoo review's first P1 finding, the drift class)",
        lambda r: _strip_closure_annotation(r),
        "VER-904",
    ),
    (
        "MUT-29",
        "regress §9 to the superseded GLM-governing form — the verification family becomes a host requirement again while D-028 stands (the Arivoo review's second P1 finding, the agent-agnostic propagation class)",
        lambda r: _glm_governing_regression(r),
        "VER-507",
    ),
    (
        "MUT-30",
        "move the worklog-tail boot step BELOW the ledger step — the coordination context no longer loads before the selective authority dive; the directory-separator path was INVISIBLE to the old parser (the Arivoo review's P3 finding), so this mutation no-ops the old VER-110 — the repaired parser must catch it",
        lambda r: _worklog_after_ledger(r),
        "VER-110",
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
    (
        "MUT-31",
        "triplicate the ledger's LAST one-liner row byte-identically — the INT-126 intake class (b572d3f): the numbering section's summary row appended twice at once, invisible to VER-201 (the header regex matches DETAILED blocks only) and deduped silently by VER-212's named set (CLAIM-030, the H-01c-claims card item (d))",
        lambda r: _one_liner_dup(r),
        "VER-213",
    ),
    (
        "MUT-32",
        "coordinated raw+manifest reanchor (the H-01c-authority card's core case): append a benign line to 2.txt AND update its manifest full-digest anchor to the new hash — the candidate controls both sides of the old comparison, so VER-802's whole-manifest grep passes; the trusted anchor map must refuse the pair",
        lambda r: _reanchor_coordinated(r),
        "VER-805",
    ),
    (
        "MUT-33",
        "move a digest to the wrong row: swap 0.txt's and 1.txt's full-digest values in the manifest — every hash still appears in the file (VER-802's grep passes), but each anchor no longer binds to its OWN file's row (the per-row placement rule)",
        lambda r: _wrong_row_digests(r),
        "VER-805",
    ),
    (
        "MUT-34",
        "fabricate a ledger quote in CURLY-quoted form (U+201C/U+201D content that exists nowhere in raw) — the old extraction matched straight double quotes only, so fabricated curly-quoted content was never checked (the card's fail-closed quote form)",
        lambda r: _curly_fabrication(r),
        "VER-803",
    ),
    (
        "MUT-35",
        "strip a raw-cited entry's quotable lines entirely (INT-083's quote replaced by a non-quotable paraphrase): source metadata WITHOUT any supported quotation must fail closed, never pass as silently-validated (the card's fail-closed case)",
        lambda r: _strip_quote_lines(r),
        "VER-803",
    ),
]


# ------------------------------------------------------------ mutation helpers
# (preserved verbatim from the predecessor suite — content and semantics
# unchanged; the ONLY change is the base-owned INT_HEADER above replacing the
# candidate-imported one, so a mutation can never be steered by candidate code)

def _edit(repo: Path, rel: str, old: str, new: str) -> None:
    p = repo / rel
    p.write_text(p.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

def _one_liner_dup(repo: Path) -> None:
    """The INT-126 intake class (b572d3f): the LAST numbering-section one-liner
    row appended byte-identically right after itself — the exact form the
    session-22 preflight found triplicated; VER-201 cannot see it (detailed
    blocks only) and VER-212's named SET dedupes it silently."""
    p = repo / "INTENT-LEDGER.md"
    text = p.read_text(encoding="utf-8")
    rows = re.findall(r"^- \*\*INT-\d{3}(?:\.\.INT-\d{3})?\*\* .*$", text, re.M)
    assert rows, "the ledger must carry one-liner rows for this mutation"
    last = rows[-1]
    # THREE byte-identical rows total (the #65 review round: the first draft
    # duplicated once; the named class is the b572d3f TRIPPLICATION — Greptile
    # P2 + CodeRabbit's suggestion, independently confirmed)
    p.write_text(text.replace(last, last + "\n" + last + "\n" + last, 1), encoding="utf-8")


def _rm(repo: Path, rel: str) -> None:
    (repo / rel).unlink()


# -------------------------------------------- H-01c-authority helpers (CLAIM-036)
# The raw/manifest lineage mutations. They operate on the FIXTURE's copies of
# the real corpus (never the tree itself) and must be robust to legitimate
# anchor updates: the digests are READ from the manifest's full-digest block
# at mutation time, never hardcoded here (a stale hard-code would no-op the
# case after a legitimate reanchor — the PR #6/#12/#17 re-target class).

def _manifest_full_digests(text: str) -> dict[str, str]:
    """Parse the manifest's 'Full SHA-256 values' block: filename -> digest."""
    digs: dict[str, str] = {}
    for m in re.finditer(r"^([\w .\-]+?)[ \t]+([0-9a-f]{64})[ \t]*$", text, re.M):
        digs[m.group(1).strip()] = m.group(2)
    return digs


def _reanchor_coordinated(repo: Path) -> None:
    raw = repo / "context" / "raw" / "2.txt"
    raw.write_text(raw.read_text(encoding="utf-8") + "coordinated reanchor probe\n", encoding="utf-8")
    new_digest = hashlib.sha256(raw.read_bytes()).hexdigest()
    mp = repo / "context" / "SOURCE-COVERAGE-MANIFEST.md"
    mtext = mp.read_text(encoding="utf-8")
    old_digest = _manifest_full_digests(mtext)["2.txt"]
    # update BOTH the full-digest block and the abbreviated row if present
    mtext = mtext.replace(old_digest, new_digest)
    mtext = re.sub(r"(\|\s*`2\.txt`\s*\|[^\n]*\|)\s*`[0-9a-f]+[\u2026 ]+[0-9a-f]+`",
                   r"\1 `reanchored`", mtext)
    mp.write_text(mtext, encoding="utf-8")


def _wrong_row_digests(repo: Path) -> None:
    mp = repo / "context" / "SOURCE-COVERAGE-MANIFEST.md"
    mtext = mp.read_text(encoding="utf-8")
    digs = _manifest_full_digests(mtext)
    d0, d1 = digs["0.txt"], digs["1.txt"]
    # swap the two full-digest VALUES (files untouched — pure row relocation)
    mtext = re.sub(r"^(0\.txt)[ \t]+" + d0 + r"[ \t]*$", r"\g<1>" + " " * max(1, 41 - len("0.txt")) + d1, mtext, flags=re.M)
    mtext = re.sub(r"^(1\.txt)[ \t]+" + d1 + r"[ \t]*$", r"\g<1>" + " " * max(1, 41 - len("1.txt")) + d0, mtext, flags=re.M)
    mp.write_text(mtext, encoding="utf-8")


def _curly_fabrication(repo: Path) -> None:
    _edit(
        repo,
        "INTENT-LEDGER.md",
        '> "1 - smallest daily loop. i read books, i import articles, posts, writings, research paper, pdfs, md\'s and any thing readable. reason through it take notes on it, and jounral about my learnings, reasoning, and reading journey how it is going and everything, and like everything compounds thats the goal since the start.. notes get compounded, everything i can comeback to, revise, and like actually learn things, develop..."',
        "> \u201c1 - biggest quarterly waterfall of fabricated curly content that exists nowhere in the raw corpus, the extraction must refuse it\u2014straight-quote blindness closed\u201d",
    )


def _strip_quote_lines(repo: Path) -> None:
    _edit(
        repo,
        "INTENT-LEDGER.md",
        '> "1 - smallest daily loop. i read books, i import articles, posts, writings, research paper, pdfs, md\'s and any thing readable. reason through it take notes on it, and jounral about my learnings, reasoning, and reading journey how it is going and everything, and like everything compounds thats the goal since the start.. notes get compounded, everything i can comeback to, revise, and like actually learn things, develop..."',
        "- (the quotation was stripped by MUT-35 — source metadata must not pass without a checkable quote)",
    )


def _tag_gate_regression(repo: Path) -> None:
    ns = repo / "NORTH-STAR.md"
    text = ns.read_text(encoding="utf-8")
    if "never a gate" not in text:
        return
    ns.write_text(text.replace("never a gate", "the deciding gate", 1), encoding="utf-8")


def _malform_header(repo: Path) -> None:
    ledger = repo / "INTENT-LEDGER.md"
    text = ledger.read_text(encoding="utf-8")
    headers = list(INT_HEADER.finditer(text))
    if not headers:
        return
    last = headers[-1]
    rebuilt = f"**INT-{last.group(1)} — {last.group(2)}**"
    ledger.write_text(text[: last.start()] + rebuilt + text[last.end():], encoding="utf-8")


def _dangling_ref(repo: Path) -> None:
    plan = repo / "PLAN.md"
    plan.write_text(
        plan.read_text(encoding="utf-8")
        + "\nProbe line (known-bad mutation): see INT-199 and D-999.\n",
        encoding="utf-8",
    )


def _count_drift(repo: Path) -> None:
    agents = repo / "AGENTS.md"
    text = agents.read_text(encoding="utf-8")
    m = re.search(r"(\d+) statused intents", text)
    if not m:
        return
    agents.write_text(
        text[: m.start(1)] + str(int(m.group(1)) - 1) + text[m.end(1):],
        encoding="utf-8",
    )


def _open_set_drift(repo: Path) -> None:
    ex = repo / "EXECUTION.md"
    text = ex.read_text(encoding="utf-8")
    rows = [
        ln
        for ln in text.splitlines()
        if re.match(r"^\|\s*(?:Q\d+|QD-\d+|D-\d{3}|F-\d+|Q-IDENT)\s*\|", ln)
    ]
    if not rows:
        return
    text = text.replace(rows[0] + "\n", "", 1)
    ex.write_text(text, encoding="utf-8")


def _reintroduce_superseded_rule(repo: Path) -> None:
    ns = repo / "NORTH-STAR.md"
    text = ns.read_text(encoding="utf-8")
    if "no tag field" not in text:
        return
    ns.write_text(text.replace("no tag field", "optional tag field", 1), encoding="utf-8")


def _blanket_ledger_boot(repo: Path) -> None:
    agents = repo / "AGENTS.md"
    text = agents.read_text(encoding="utf-8")
    out = []
    for ln in text.splitlines(keepends=True):
        if re.match(r"^\s*\d+\.\s", ln) and "INTENT-LEDGER.md" in ln:
            num = ln.split(".")[0]
            ln = f"{num}. `/INTENT-LEDGER.md` — owner words, verbatim, statused. The highest authority. Load it BEFORE forming any understanding of the task.\n"
        out.append(ln)
    agents.write_text("".join(out), encoding="utf-8")


def _drop_read_order_step(repo: Path, marker: str) -> None:
    agents = repo / "AGENTS.md"
    text = agents.read_text(encoding="utf-8")
    out = [
        ln
        for ln in text.splitlines(keepends=True)
        if not (re.match(r"^\s*\d+\.\s", ln) and marker in ln)
    ]
    agents.write_text("".join(out), encoding="utf-8")


def _drop_verification_rule(repo: Path) -> None:
    agents = repo / "AGENTS.md"
    text = agents.read_text(encoding="utf-8")
    out = [ln for ln in text.splitlines(keepends=True) if "INT-070" not in ln]
    agents.write_text("".join(out), encoding="utf-8")


def _strip_closure_annotation(repo: Path) -> None:
    d = repo / "DECISIONS.md"
    text = d.read_text(encoding="utf-8")
    if "Update 2026-10-14 (D-028)" not in text:
        return
    d.write_text(
        text.replace("Update 2026-10-14 (D-028)", "Update 2026-10-14", 1),
        encoding="utf-8",
    )


def _glm_governing_regression(repo: Path) -> None:
    om = repo / "OPERATING-MODEL.md"
    text = om.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    hits = [i for i, ln in enumerate(lines)
            if "host-agnostic (D-028)" in ln and "INT-070" in ln and "GLM" in ln]
    if not hits:
        return
    OLD = (
        "The verification family is GLM-based subagents (INT-070, governing): a "
        "different model family CAN add optional adversarial coverage, but it is "
        "never a required gate and never overrides the declared GLM workflow.\n"
    )
    lines[hits[0]] = OLD
    om.write_text("".join(lines), encoding="utf-8")


def _worklog_after_ledger(repo: Path) -> None:
    agents = repo / "AGENTS.md"
    text = agents.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    wl = [i for i, ln in enumerate(lines)
          if re.match(r"^\s*\d+\.\s", ln) and "context/WORKLOG.md" in ln]
    lg = [i for i, ln in enumerate(lines)
          if re.match(r"^\s*\d+\.\s", ln) and "INTENT-LEDGER.md" in ln]
    if not wl or not lg:
        return
    wl_i, lg_i = wl[0], lg[0]
    if wl_i == lg_i:
        return
    wl_line, lg_line = lines[wl_i], lines[lg_i]
    wl_num = re.match(r"^\s*(\d+\.)\s", wl_line).group(1)
    lg_num = re.match(r"^\s*(\d+\.)\s", lg_line).group(1)
    lines[wl_i] = lg_line.replace(lg_num, wl_num, 1)
    lines[lg_i] = wl_line.replace(wl_num, lg_num, 1)
    agents.write_text("".join(lines), encoding="utf-8")


def _drop_ledger_step(repo: Path) -> None:
    agents = repo / "AGENTS.md"
    text = agents.read_text(encoding="utf-8")
    out = [
        ln
        for ln in text.splitlines(keepends=True)
        if not (re.match(r"^\s*\d+\.\s", ln) and "INTENT-LEDGER.md" in ln)
    ]
    agents.write_text("".join(out), encoding="utf-8")


def _stale_state_pointer(repo: Path) -> None:
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


# ------------------------------------------------------------ the H-01b delegation
# The machinery (bounded fixtures, integrity, child runner, protocol, manifest)
# lives in tools/mutation_runner.py — the card's named runner module, landed as
# H-01b part 1 (PR #47). This driver owns the base-owned MUTATION REGISTRY and
# the CLI; the runner is loaded BY PATH (never via sys.path), which works under
# `python3 -I` and keeps the module boundary honest.

def _load_runner():
    import importlib.util
    runner_path = Path(__file__).resolve().parent / "mutation_runner.py"
    spec = importlib.util.spec_from_file_location("ariv_mutation_runner", runner_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, runner_path


def _select(only: str | None) -> list:
    """Case selection against THIS module's registry (base-owned state — an
    unknown/duplicate/empty selection refuses, fail-closed)."""
    if not only:
        return list(MUTATIONS)
    wanted = [w.strip() for w in only.split(",") if w.strip()]
    if not wanted:
        raise SystemExit("refused: --only must name at least one case (MUT-XX)")
    if len(set(wanted)) != len(wanted):
        raise SystemExit("refused: --only must not repeat a case")
    by_code = {m[0]: m for m in MUTATIONS}
    sel = []
    for w in wanted:
        if not re.fullmatch(r"MUT-\d{2}", w) or w not in by_code:
            raise SystemExit(f"refused: unknown case '{w}' — the expected set is fixed (MUT-01..MUT-35)")
        sel.append(by_code[w])
    return sel


def self_test(repo: Path | None = None, only: str | None = None,
              floor_base: str | None = None, manifest_out: Path | None = None,
              case_timeout: int | None = None) -> int:
    """The floor entry (verify_canonical_layer.py --self-test delegates here).
    `repo` is accepted for backward compatibility but is NEVER the authority:
    the corpus root is computed from THIS file's location (the caller-supplied
    path was part of the A03 hole)."""
    del repo
    runner, _rp = _load_runner()
    cases = _select(only)
    return runner.run_floor(
        cases, REPO,
        driver_path=Path(__file__).resolve(),
        sibling_module=Path(__file__).resolve().parent / "mutation_runner.py",
        floor_base=floor_base,
        manifest_out=manifest_out,
        case_timeout=case_timeout if case_timeout is not None else runner.DEFAULT_CASE_TIMEOUT,
    )


def main(argv=None) -> int:
    runner, _rp = _load_runner()
    ap = argparse.ArgumentParser(description="the H-01b trusted candidate-tool execution floor")
    ap.add_argument("--repo", default=None, help="the candidate tree to judge (default: this driver's own tree)")
    ap.add_argument("--only", default=None, help="run only the named case(s), e.g. MUT-04,MUT-13 (test-side subsetting; CI runs the full set)")
    ap.add_argument("--floor-base", default=None, help="the trusted base tools directory (CI passes base/tools via ARV_FLOOR_BASE_TOOLS or this flag)")
    ap.add_argument("--manifest-out", default=None, help="where to write the completion manifest")
    ap.add_argument("--case-timeout", type=int, default=runner.DEFAULT_CASE_TIMEOUT, help="per-case wall-clock seconds")
    ap.add_argument("--validate-manifest", default=None, help="validate an EXTERNAL manifest file against the expected case set (the public validator surface — exit 0/1, ARV-FLOOR-006 named refusals); --only selects the expected set")
    a = ap.parse_args(argv)
    if a.validate_manifest:
        import json
        try:
            m = json.loads(Path(a.validate_manifest).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            print(f"FAIL ARV-FLOOR-006: the manifest file is unreadable or malformed JSON ({type(exc).__name__}) — refusing")
            return 1
        expected = [c[0] for c in _select(a.only)]
        fails = runner.validate_manifest(m, expected)
        if fails:
            for f in fails:
                print(f"FAIL {f}")
            return 1
        print(f"OK ARV-FLOOR-006: the manifest validates — every one of {len(expected)} expected case(s) present exactly once, records well-formed")
        return 0
    global REPO
    if a.repo is not None:
        # explicit candidate selection (tests / explicit runs). The corpus the
        # floor judges is a DRIVER-AUTHORITY input, never candidate-supplied.
        REPO = Path(a.repo).resolve()
    return self_test(only=a.only, floor_base=a.floor_base,
                     manifest_out=Path(a.manifest_out) if a.manifest_out else None,
                     case_timeout=a.case_timeout)


if __name__ == "__main__":
    sys.exit(main())
