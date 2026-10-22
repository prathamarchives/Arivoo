#!/usr/bin/env python3
"""harness/claims.py — the claims-registry checks (D-038/LAW-31; session 19, CLAIM-002).

The ratchet response to the session-19 two-agent collision (record 19 §8): the
registry CLAIMS.md exists so concurrent agents cannot silently work the same
files, and these checks make the registry's rules mechanically enforced at the
gate. Named codes (the diagnostics contract):

  ARV-CLM-001  the registry EXISTS and its tables parse (fail-closed — a missing
               or unparseable CLAIMS.md is never a silent pass)
  ARV-CLM-002  scope discipline: two OPEN claims MUST NOT overlap on any
               non-shared file (the later claim is the offender), and in PR mode
               a claim's declared scope MUST cover its actual diff — the
               claim-before-work rule. The shared-append class (the ledgers,
               the worklog, the registry, the manifest, STATE, session records
               under their own IDs) is overlap-legal: the append-only law is
               the concurrency discipline for those.
  ARV-CLM-003  INT reservations are unique among OPEN claims, and each fresh
               reservation is exactly ledger-max+1; a retroactive reservation
               (an ID already ledgered at open time) is legal ONLY with the
               retroactive notation in the row's Notes.
  ARV-CLM-004  every OPEN row is well-formed: claim ID, session, agent, branch,
               scope all present, and the branch carries the claim ID
               (slice/<claim-id-lowercase>-<slug>) — one claim, one branch.
  ARV-CLM-005  PR mode: a diff whose branch carries NO open claim is unclaimed
               work — refused (the collision class itself).

Scope entries use path-prefix semantics (the same convention as the slice
declarations): an entry names a file or a directory prefix (a trailing '/'
entry covers everything under it).
"""
import os
import pathlib
import re


def _repo_root() -> pathlib.Path:
    """H-01b-CI (session 23): ARV_TRUSTED_ROOT re-roots this machinery onto the
    candidate tree when the trusted gate driver has validated it (absolute
    existing dir only; anything else keeps the natural root)."""
    root = os.environ.get("ARV_TRUSTED_ROOT", "")
    p = pathlib.Path(root) if root else None
    if p is not None and p.is_absolute() and p.is_dir():
        return p
    return pathlib.Path(__file__).resolve().parents[1]


REPO = _repo_root()
LEDGER = "INTENT-LEDGER.md"

# the files any claim may touch (append-shaped only — CLAIMS.md rule 2)
SHARED_APPEND = (
    "INTENT-LEDGER.md", "DECISIONS.md", "context/WORKLOG.md", "CLAIMS.md",
    "STATE.md", "context/SOURCE-COVERAGE-MANIFEST.md",
)

_COLS = ("| Claim |", "| Session |", "| Agent |", "| Branch |",
         "| Scope (globs) |", "| INTs reserved |", "| Opened |")


def _cells(row: str) -> list:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def _open_rows(text: str) -> list:
    """Parse the '## Open claims' table rows into dicts (fail-closed on shape)."""
    m = re.search(r"^## Open claims\s*$", text, re.M)
    if not m:
        return []
    tail = text[m.end():]
    m2 = re.search(r"^## ", tail, re.M)
    section = tail[:m2.start()] if m2 else tail
    rows = []
    for ln in section.splitlines():
        s = ln.strip()
        if not s.startswith("|") or set(s) <= {"|", "-", " ", ":"}:
            continue  # separator or blank
        cells = _cells(s)
        if len(cells) < 8 or cells[0].startswith("*"):
            continue
        if cells[0].strip().lower() == "claim":
            continue  # the header row (fail-closed shape check verified it separately)
        rows.append({
            "claim": cells[0], "session": cells[1], "agent": cells[2],
            "branch": cells[3], "scope": cells[4], "ints": cells[5],
            "opened": cells[6], "notes": cells[7] if len(cells) > 7 else "",
            "raw": s,
        })
    return rows


def _scope_entries(scope_cell: str) -> list:
    return [e.strip().strip("`") for e in scope_cell.split(",") if e.strip().strip("`")]


def _covers(entry: str, path: str) -> bool:
    """Path-prefix semantics: a file equals the entry or lives under its directory."""
    ent = entry.rstrip("/")
    if not ent:
        return False
    return path == ent or path.startswith(ent + "/")


def _shared(path: str) -> bool:
    return any(path == s or path.startswith(s + "/") or path.startswith(s)
               for s in SHARED_APPEND)


def _reservations(ints_cell: str) -> list:
    """The bare INT-<n> tokens of the reservation column (parenthetical prose ignored)."""
    bare = re.sub(r"\([^)]*\)", "", ints_cell)
    return re.findall(r"INT-(\d+)", bare)


def _ledger_max(repo: pathlib.Path) -> int:
    text = (repo / LEDGER).read_text(encoding="utf-8")
    nums = [int(n) for n in re.findall(r"INT-(\d+)", text)]
    return max(nums) if nums else 0


def _print_fail(code: str, msg: str, repair: str) -> None:
    print(f"FAIL {code}: {msg}")
    print(f"      repair: {repair}")


def _closed_row_ids(text: str) -> list:
    """The claim IDs of the Closed table, MULTIPLICITY PRESERVED — R-04(9):
    the intra-table duplicate class (the duplicate CLAIM-021 closed rows,
    G-58-1) is invisible to a set, which silently deduplicates the very
    drift ARV-CLM-007 exists to name."""
    m = re.search(r"^## Closed claims\s*$", text, re.M)
    if not m:
        return []
    ids = []
    for ln in text[m.end():].splitlines():
        s = ln.strip()
        if not s.startswith("|") or set(s) <= {"|", "-", " ", ":"}:
            continue
        cells = _cells(s)
        if cells and cells[0].strip().lower() != "claim" and not cells[0].startswith("*"):
            ids.append(cells[0].strip())
    return ids


def _closed_ids(text: str) -> set:
    """The claim IDs of the Closed table (first cell per row). H-01c-claims:
    the WHOLE registry is swept — the diff-scoped checks missed the
    both-tables drift for three PRs (CLAIM-007, record 22 §2)."""
    return set(_closed_row_ids(text))


def _dups(ids: list) -> list:
    """The IDs appearing MORE THAN ONCE, first-repeated order (R-04(9))."""
    seen, dup = set(), []
    for x in ids:
        if x in seen and x not in dup:
            dup.append(x)
        seen.add(x)
    return dup


def check_registry(repo: pathlib.Path = REPO) -> list:
    """ARV-CLM-001..004 over the OPEN table + 006/007 registry-wide (the
    both-tables and intra-table duplicate classes). Returns the fail codes."""
    fails = []
    p = repo / "CLAIMS.md"
    if not p.is_file():
        _print_fail("ARV-CLM-001", "CLAIMS.md is missing — LAW-31's substrate does not exist (fail-closed)",
                    "commit the claims registry (D-038) — a missing registry is never a silent pass")
        return ["ARV-CLM-001"]
    text = p.read_text(encoding="utf-8")
    if not all(c in text for c in _COLS):
        _print_fail("ARV-CLM-001", "the Open-claims table is malformed (the expected columns are absent)",
                    "restore the registry table: | Claim | Session | Agent | Branch | Scope (globs) | INTs reserved | Opened | Notes |")
        return ["ARV-CLM-001"]
    rows = _open_rows(text)
    closed_ids = _closed_ids(text)
    # ARV-CLM-007 — the INTRA-TABLE duplicate ratchet (R-04(9), G-58-1): the
    # same claim ID TWICE in ONE table is registry drift; the duplicate
    # CLAIM-021 closed rows survived every check because ARV-CLM-006 covers
    # only the BOTH-TABLES class. Multiplicity is the signal — never dedupe
    # it away. Both tables, one code: the drift class is the same either side.
    open_ids = [r["claim"] for r in rows]
    for cid in _dups(open_ids):
        _print_fail("ARV-CLM-007",
                    f"{cid}: appears {open_ids.count(cid)} times in the OPEN table — intra-table registry drift (the duplicate-CLAIM-021 closed-row class, G-58-1; R-04(9))",
                    "one row per claim per table: merge the duplicate rows through the rule-4 reconciliation protocol in the next slice's PR, recording the merge in the claim's closed row")
        fails.append("ARV-CLM-007")
    closed_row_ids = _closed_row_ids(text)
    for cid in _dups(closed_row_ids):
        _print_fail("ARV-CLM-007",
                    f"{cid}: appears {closed_row_ids.count(cid)} times in the CLOSED table — intra-table registry drift (the duplicate-CLAIM-021 closed-row class, G-58-1; R-04(9))",
                    "one row per claim per table: merge the duplicate rows through the rule-4 reconciliation protocol in the next slice's PR, recording the merge in the claim's closed row")
        fails.append("ARV-CLM-007")
    lmax = _ledger_max(repo)
    seen_res: dict = {}
    for r in rows:
        # ARV-CLM-006 — registry-wide duplicate detection (H-01c-claims): an
        # ID in BOTH tables is drift; the diff-scoped checks can never see it
        if r["claim"] in closed_ids:
            _print_fail("ARV-CLM-006",
                        f"{r['claim']}: present in BOTH the open and closed tables — registry drift (the CLAIM-007 class: a merged claim's stale open row surviving diff-scoped checks)",
                        "reconcile the registry through the rule-4 protocol: append the closed row and retire the open row in the next slice's PR, recording the reconciliation")
            fails.append("ARV-CLM-006")
        # ARV-CLM-004 — well-formedness
        blanks = [k for k in ("claim", "session", "agent", "branch", "scope") if not r[k]]
        want = "slice/" + r["claim"].strip().lower() + "-"
        if blanks or not r["branch"].strip("`").startswith(want):
            _print_fail("ARV-CLM-004",
                        f"{r['claim'] or '(unnamed)'}: a malformed OPEN row (blanks={blanks or 'none'}; branch '{r['branch']}' does not carry the claim id)",
                        "every OPEN row carries claim id, session, agent, branch (slice/<claim-id-lowercased>-<slug>), and scope — one claim, one branch, one PR")
            fails.append("ARV-CLM-004")
        # ARV-CLM-003 — reservations
        for n in _reservations(r["ints"]):
            if n in seen_res:
                _print_fail("ARV-CLM-003",
                            f"{r['claim']}: INT-{n} is already reserved by {seen_res[n]} — duplicate reservation (the merge-order race)",
                            "reserve exactly previous-max+1 of the used set, one at a time; a collision amends the LATER claim pre-merge")
                fails.append("ARV-CLM-003")
            else:
                seen_res[n] = r["claim"]
            v = int(n)
            if v > lmax and v != lmax + 1:
                _print_fail("ARV-CLM-003",
                            f"{r['claim']}: INT-{n} is not the next free id (ledger max is INT-{lmax}; the next fresh reservation is INT-{lmax + 1})",
                            "reserve ledger-max+1; a retroactive reservation (an already-ledgered id) requires the retroactive notation in Notes")
                fails.append("ARV-CLM-003")
            if v <= lmax and "retroactiv" not in (r["ints"] + " " + r["notes"]).lower():
                _print_fail("ARV-CLM-003",
                            f"{r['claim']}: INT-{n} is already ledgered but the row does not carry the retroactive notation",
                            "a reservation of an already-ledgered id must be marked retroactive in Notes (honesty rule, CLAIMS.md 6)")
                fails.append("ARV-CLM-003")
    # ARV-CLM-002 — pairwise scope exclusivity on non-shared files
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = rows[i], rows[j]
            for ea in _scope_entries(a["scope"]):
                for eb in _scope_entries(b["scope"]):
                    if _shared(ea) or _shared(eb):
                        continue
                    if ea == eb or ea.startswith(eb.rstrip("/") + "/") or eb.startswith(ea.rstrip("/") + "/"):
                        _print_fail("ARV-CLM-002",
                                   f"{b['claim']} overlaps {a['claim']} on '{ea}' (a non-shared file) — two OPEN claims may not overlap",
                                   "the later claim narrows its scope or waits; the shared-append class is exempt (append-shaped edits only)")
                        fails.append("ARV-CLM-002")
    return sorted(set(fails))


def check_branch_claim(branch: str, diff: list, repo: pathlib.Path = REPO) -> list:
    """ARV-CLM-005 + the PR-mode side of ARV-CLM-002: the branch's open claim must
    exist and its declared scope must cover the actual diff (claim-before-work)."""
    fails = []
    p = repo / "CLAIMS.md"
    if not p.is_file():
        return check_registry(repo)  # ARV-CLM-001 already fires
    rows = _open_rows(p.read_text(encoding="utf-8"))
    row = next((r for r in rows if r["branch"].strip("`") == branch), None)
    if row is None:
        _print_fail("ARV-CLM-005",
                    f"branch '{branch}' carries NO open claim — unclaimed work (the session-19 collision class)",
                    "the first work commit carries the claim row (CLAIMS.md); one claim, one branch, one PR")
        return ["ARV-CLM-005"]
    entries = _scope_entries(row["scope"])
    for path in diff:
        if not any(_covers(e, path) for e in entries):
            _print_fail("ARV-CLM-002",
                        f"{row['claim']}: the diff touches '{path}' OUTSIDE its declared scope",
                        "declare the scope honestly (path prefixes; the shared-append class only for append-shaped edits) or split the work into its own claim")
            fails.append("ARV-CLM-002")
    return sorted(set(fails))


if __name__ == "__main__":
    import sys
    bad = check_registry() + (check_branch_claim(sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else [])
    print()
    if bad:
        print(f"RED — the claims checks refuse: {', '.join(bad)}")
        sys.exit(1)
    print("GREEN — the registry parses, exclusivity holds, reservations are sound")
