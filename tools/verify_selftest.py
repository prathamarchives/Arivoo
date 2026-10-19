#!/usr/bin/env python3
"""verify_selftest.py — the canonical-layer self-test, as a separately-invocable module.

Extracted from tools/verify_canonical_layer.py (session 17, D-035 — the
candidate-tool gate repair): the MUTATION SUITE and the VERIFIER can now be
anchored independently, so the base-anchored CI job runs THIS suite (from main)
against the CANDIDATE's verify_canonical_layer.py — the coordinated-weakening
floor (a PR that weakens the verifier AND its own mutation suite together fails
these cases in the required job).

This module imports Layer (and its entry-header pattern) from
verify_canonical_layer — WHICHEVER implementation sits beside it. That is the
point: the base's suite judging the candidate's implementation. Content and
semantics are moved verbatim (30 mutations; counts unchanged). The mutation
helpers that no-op (e.g. a weakened _edit) are themselves caught: the self-test
RED-flags a no-op mutation as a blind guard by design.

Usage: python3 tools/verify_selftest.py   (or verify_canonical_layer.py
--self-test, which delegates here for backward compatibility).
"""

from __future__ import annotations

import re
import shutil
import sys
import tempfile
from pathlib import Path

from verify_canonical_layer import INT_HEADER, REPO, Layer

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
]


def _edit(repo: Path, rel: str, old: str, new: str) -> None:
    p = repo / rel
    p.write_text(p.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")


def _rm(repo: Path, rel: str) -> None:
    (repo / rel).unlink()


def _tag_gate_regression(repo: Path) -> None:
    """MUT-11, content-generic (re-targeted 2026-10-14, session 15 — the same repair
    class as MUT-08/MUT-17, PRs #6/#12): rewrite the first 'never a gate' occurrence
    in NORTH-STAR into a gate form, whatever the surrounding sentence says. The
    earlier hard-coded string would silently no-op after the tag-removal rewording
    (INT-112/D-030) — a no-op mutation reads as a blind guard and RED-blocks the
    legitimate rewording PRs."""
    ns = repo / "NORTH-STAR.md"
    text = ns.read_text(encoding="utf-8")
    if "never a gate" not in text:
        return
    ns.write_text(text.replace("never a gate", "the deciding gate", 1), encoding="utf-8")


def _malform_header(repo: Path) -> None:
    """MUT-23, content-generic: strip the status segment from the highest-numbered
    well-formed entry header. The strict INT_HEADER view stops seeing the entry
    (VER-201/202 go blind for it) while the loose entry splitter still finds it —
    VER-903 must catch the two-view disagreement (the malformed-header blind spot
    the slice-7 audit found: the two parsing patterns disagreed silently)."""
    ledger = repo / "INTENT-LEDGER.md"
    text = ledger.read_text(encoding="utf-8")
    headers = list(INT_HEADER.finditer(text))
    if not headers:
        return
    last = headers[-1]
    rebuilt = f"**INT-{last.group(1)} — {last.group(2)}**"
    ledger.write_text(text[: last.start()] + rebuilt + text[last.end():], encoding="utf-8")


def _dangling_ref(repo: Path) -> None:
    """MUT-24: append a probe line to PLAN.md citing INT-199 and D-999 — neither
    exists. VER-901 must fail on the dangling references (the referenced-IDs-must-
    exist requirement, slice 7)."""
    plan = repo / "PLAN.md"
    plan.write_text(
        plan.read_text(encoding="utf-8")
        + "\nProbe line (known-bad mutation): see INT-199 and D-999.\n",
        encoding="utf-8",
    )


def _count_drift(repo: Path) -> None:
    """MUT-25, content-generic: decrement the first stated statused-intent count in
    AGENTS.md — the summary drifts from the observed ledger; VER-902 must catch the
    contradiction (a stale count is not a snapshot)."""
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
    """MUT-26, content-generic: remove the FIRST open-question table row in
    EXECUTION §6 — the open register disagrees across its mirrors; the re-targeted
    VER-504 must catch it (a closure by silent removal, never by a D-row). If the
    §6 table ever legitimately changes shape, this no-ops and the self-test reports
    a blind guard — the designed re-target alarm."""
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
    """MUT-27 (slice 9, class (d) — sub-agent finding 1): rewrite NORTH-STAR's
    current-truth phrase 'no tag field' into the superseded optional-tag form. This
    is the reintroduced-known-conflicting-rule class: the mutation leaves the C4
    marker line intact and keeps the F-05 qualifier, so every substring guard
    except the normative-marker register stays green — VER-904 must fail."""
    ns = repo / "NORTH-STAR.md"
    text = ns.read_text(encoding="utf-8")
    if "no tag field" not in text:
        return
    ns.write_text(text.replace("no tag field", "optional tag field", 1), encoding="utf-8")


def _blanket_ledger_boot(repo: Path) -> None:
    """MUT-21, content-generic: rewrite the numbered read-order line naming
    INTENT-LEDGER.md into the blanket ledger-first form — whatever the line currently
    says (old order or selective order), the SELECTIVE marker must disappear so VER-110
    catches the silent regression. Content-generic for the same reason as MUT-08/MUT-17:
    a hard-coded current string would no-op after any future rewording."""
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
    """MUT-22: remove the numbered read-order line containing `marker` (the worklog-tail
    boot step). Generic over the line's current wording."""
    agents = repo / "AGENTS.md"
    text = agents.read_text(encoding="utf-8")
    out = [
        ln
        for ln in text.splitlines(keepends=True)
        if not (re.match(r"^\s*\d+\.\s", ln) and marker in ln)
    ]
    agents.write_text("".join(out), encoding="utf-8")


def _drop_verification_rule(repo: Path) -> None:
    """MUT-05, content-generic (re-targeted 2026-10-14, session 16 / D-034 — the same
    repair class as MUT-08/MUT-11/MUT-17, PRs #6/#12/#17): remove every AGENTS.md line
    carrying INT-070, whatever the line currently says. The earlier hard-coded string
    ("Test and verification loops run on GLM-based subagents; ...") would silently
    no-op the moment the agent-agnostic rewording lands (D-028's propagation, the
    Arivoo review's P1 finding) — a no-op mutation reads as a blind guard and
    RED-blocks the legitimate rewording PR. Generic form: works on every wording
    that keeps the verification protocol's INT-070 reference."""
    agents = repo / "AGENTS.md"
    text = agents.read_text(encoding="utf-8")
    out = [ln for ln in text.splitlines(keepends=True) if "INT-070" not in ln]
    agents.write_text("".join(out), encoding="utf-8")


def _strip_closure_annotation(repo: Path) -> None:
    """MUT-28 (session 16, D-034 — the Arivoo review's first P1 finding): strip the
    D-028 closure pointer from D-007's update note in DECISIONS.md. The closed
    question then reads as OPEN again in a current canonical document (the drift
    class the review found); VER-904's closure-marker register must catch it."""
    d = repo / "DECISIONS.md"
    text = d.read_text(encoding="utf-8")
    if "Update 2026-10-14 (D-028)" not in text:
        return
    d.write_text(
        text.replace("Update 2026-10-14 (D-028)", "Update 2026-10-14", 1),
        encoding="utf-8",
    )


def _glm_governing_regression(repo: Path) -> None:
    """MUT-29 (session 16, D-034 — the Arivoo review's second P1 finding): revert
    OPERATING-MODEL §9's host-agnostic verification-protocol line to the superseded
    GLM-governing form, while D-028 (agent-agnostic) still stands — the
    reintroduced-known-conflicting-rule class. CONTENT-GENERIC since 2026-10-19
    (session 19 — a legitimate §9 rewording by a concurrent part made the exact-
    string form silently no-op; the base-anchored suite RED-flagged it as a blind
    guard — the PR #6/#12/#17/#19 re-target class): the mutation now locates the
    §9 protocol line by its stable markers ('host-agnostic (D-028)' + 'INT-070' +
    'GLM') and replaces that whole line, so a legitimate rewording cannot silently
    no-op it. The strict §9-scoped VER-507 must catch the regression ('current
    default' vanishes from §9); a valid alternative-host declaration (the positive
    case) passes."""
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
    """MUT-30 (session 16, D-034 — the Arivoo review's P3 finding): swap the bodies of
    the context/WORKLOG.md and INTENT-LEDGER.md read-order steps (numbers stay
    well-formed), so the ledger step loads BEFORE the worklog tail — the coordination
    context no longer precedes the selective authority dive. The old read-order
    parser could not match paths containing a directory separator, so the worklog
    step was invisible to position checks — this ordering regression was unenforceable
    (a blind guard). The repaired parser + strengthened VER-110 must catch it."""
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
    """MUT-08, content-generic (2026-10-14, session-14 gate re-target): remove the numbered
    read-order line that names /INTENT-LEDGER.md. The earlier form replaced a hard-coded
    ledger-first step-1 string; once AGENTS' read order moves the ledger off step 1 (the
    slice-6 supersession, D-027(3)/INT-107), that string stops matching, the mutation
    silently no-ops, VER-101 does not fail, and the base-anchored self-test reports a blind
    guard — RED-blocking the very PR that legitimately changes the boot order. Generic form:
    works on every read order that keeps a numbered INTENT-LEDGER step, current or future
    (the same repair class as MUT-17's genericization, PR #6)."""
    agents = repo / "AGENTS.md"
    text = agents.read_text(encoding="utf-8")
    out = [
        ln
        for ln in text.splitlines(keepends=True)
        if not (re.match(r"^\s*\d+\.\s", ln) and "INTENT-LEDGER.md" in ln)
    ]
    agents.write_text("".join(out), encoding="utf-8")


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






if __name__ == "__main__":
    sys.exit(self_test(REPO))
