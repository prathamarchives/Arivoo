#!/usr/bin/env python3
r"""harness/migrate.py — the forward-only migrations runner + the M0 migration
oracle (S1; D-036; P3-M0 — PLAN's P3-M0 card, RTM §5, the §6.2 eight-point
contract; F-009/F-010 RED-first; the SEV/#82 rounds' repairs).

Contract (mechanical; every failure prints rule ID + what + repair):
  * forward-only, versioned NNNN_name.sql from a gapless baseline 0001
  * safe names: [0-9]{4}_[a-z][a-z0-9_]*.sql (ARV-MIG-014 at discovery —
    within the alphabet the ledger INSERT's literal is provably safe; psql
    has no parameter binding, so the alphabet IS the reliable quoting, F-010)
  * applied-file immutability (ARV-MIG-005); destructive statements require
    '-- arv-baseline-bump: <n>' (ARV-MIG-003, comment-proof + token-proof)
  * the runner owns the ONE transaction boundary: embedded transaction
    control refused pre-execution at statement-head level, directive-proof
    (ARV-MIG-011 — END included: PG's own COMMIT synonym)
  * the ADMITTED GRAMMAR fails closed (ARV-MIG-015): constructs the checker
    cannot classify (procedural/dynamic, data-modifying bodies) require the
    directive; the DECLARED 0001_baseline bootstrap exemption is name-scoped
    (exactly version 1, name 'baseline'; its text is still scanned for
    transaction control and destructive statements)
  * bidirectional directory<->ledger history, BOTH paths (ARV-MIG-012):
    extra rows, interior holes, name drift; the ledger parser fails closed on
    unparseable rows (ARV-MIG-007 — a poisoned row is never invisible)
  * --verify is observation-only (ARV-MIG-013: a missing ledger is an honest
    refusal, never a CREATE side effect)
  * the pending-file pre-scan: every file about to run passes the oracle
    BEFORE the first DB write — a refusal leaves the DB untouched; each file
    applies inside ONE transaction together with its bookkeeping row
  * re-runnable: nothing to apply is a no-op (ARV-MIG-001); --verify
    re-checks every checksum

The scanner (F-009): a character-level mask — line/nested-block comments,
strings, E-strings, quoted identifiers, dollar-quoted bodies — runs before
every keyword scan. Identifier context is tracked EXACTLY as PG's byte-
oriented scan.l (any codepoint >= U+0080 starts/continues an identifier,
astral planes included): '$' inside an identifier never opens a dollar-quote
(the SEV rounds' phantom-quote P0s, closed). Unterminated constructs fail
closed (ARV-MIG-016). The residual lexer-drift classes (hex adjacency,
E-space/nameE shapes, high-bit dollar-tags, U& spellings) are fail-closed
over-refusals only — named at the runs dir's notverified.txt.

Exit 0 = ok; exit 1 = refusal/failure.
"""
import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.adapters import pg  # noqa: E402

SAFE_NAME_RE = re.compile(r"^(\d{4})_([a-z][a-z0-9_]*)\.sql$")  # F-010: the safe alphabet
DESTRUCTIVE_RE = re.compile(r"(?i)\b(DROP\s+TABLE|DROP\s+COLUMN|DROP\s+SCHEMA|TRUNCATE|ALTER\s+TABLE(\s+IF\s+EXISTS)?\s+\S+\s+DROP|DELETE\s+FROM)\b")
DATA_MODIFY_RE = re.compile(r"(?i)\b(INSERT\s+INTO|UPDATE(?:\s+\S+){1,3}\s+SET|DELETE\s+FROM|MERGE\s+INTO|SELECT\s+INTO)\b")
BUMP_RE = re.compile(r"(?m)^\s*--\s*arv-baseline-bump:\s*(\d+)")
DOLLAR_OPEN_RE = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)?\$")

# The character classes of PG's lexer (scan.l) — BYTE-ORIENTED, never
# codepoint-capped (the re-review's SEV-10: PG continues identifiers through
# every high-bit byte, astral planes included; a \uFFFF cap re-opened the
# phantom dollar-quote one Unicode level up). An identifier STARTS with
# [_A-Za-z] or ANY codepoint >= U+0080, and CONTINUES with those + [0-9$].
# The SEV-1 rule: a '$' inside an identifier NEVER opens a dollar-quote
# ('b$$c' — and 'c\U0001F600$$' — are ONE identifier to PG).


def _ident_start(ch: str) -> bool:
    return ch == "_" or "A" <= ch <= "Z" or "a" <= ch <= "z" or ord(ch) >= 0x80


def _ident_cont(ch: str) -> bool:
    return _ident_start(ch) or ch in "0123456789$"

# The admitted grammar: heads classifiable as non-procedural. Everything else
# fails closed to ARV-MIG-015 without the directive (procedural/dynamic SQL is
# never admitted by classification — only by the owner-visible directive, or
# the name-scoped baseline exemption). _DROP_IFEXISTS: the idempotent-recreate
# pattern the substrate migrations use.
_PLAIN_CREATE = {"TABLE", "INDEX", "SCHEMA", "SEQUENCE", "VIEW", "TRIGGER",
                 "POLICY", "ROLE", "TYPE", "EXTENSION", "COLLATION", "DOMAIN"}
_PROCEDURAL_CREATE = {"FUNCTION", "PROCEDURE", "AGGREGATE"}
_DROP_IFEXISTS = {"TRIGGER", "POLICY", "INDEX", "VIEW"}
_CREATE_SKIP = {"OR", "REPLACE", "UNIQUE", "TEMP", "TEMPORARY", "IF", "NOT", "CONSTRAINT"}


class ScanError(Exception):
    """An unterminated construct: the mask cannot be trusted, so the file is
    refused fail-closed (ARV-MIG-016)."""


def _die(code: str, what: str, repair: str) -> "None":
    print(f"FAIL {code}: {what}")
    print(f"      repair: {repair}")
    sys.exit(1)


def mask(text: str) -> str:
    """The character-level mask (F-009): comments, strings, E-strings, quoted
    identifiers and dollar-quoted bodies become fixed placeholders; everything
    else passes through. PG-lexer fidelity: identifier context is tracked
    exactly as scan.l (byte-oriented — any codepoint >= U+0080 continues an
    identifier, astral planes included: 'b$$c' and 'c\U0001F600$$' are ONE
    identifier, so '$' inside an identifier never opens a dollar-quote; '$'
    after a NUMBER still does); E'...' processes backslash escapes always (the
    E must be glued to the quote, not an identifier tail). Unterminated
    constructs raise ScanError (fail closed). Admitted drift (notverified.txt):
    hex-adjacent '$', E-space/nameE shapes, high-bit dollar-tags, U& spellings
    — over-refusal/both-reject only.
    """
    out = []
    i, n = 0, len(text)
    in_ident = False
    while i < n:
        ch = text[i]
        if text.startswith("--", i):          # line comment (to EOL; content never scanned)
            j = text.find("\n", i)
            i = n if j == -1 else j
            out.append(" ")
            in_ident = False
        elif text.startswith("/*", i):        # block comment (NESTED, per SQL)
            depth, i = 1, i + 2
            while i < n and depth:
                if text.startswith("*/", i):
                    depth -= 1
                    i += 2
                elif text.startswith("/*", i):
                    depth += 1
                    i += 2
                else:
                    i += 1
            if depth:
                raise ScanError("unterminated block comment")
            out.append(" ")
            in_ident = False
        elif ch == "'":                        # single-quoted string ('' escape;
            # E'...' processes backslash escapes ALWAYS (SEV-6): the E must be
            # immediately before the quote, not the tail of an identifier
            prev = text[i - 1] if i else ""
            pre_prev = text[i - 2] if i > 1 else ""
            escaped = prev in ("E", "e") and not (pre_prev and _ident_cont(pre_prev))
            i += 1
            while i < n:
                if escaped and text[i] == "\\":
                    i += 2
                    continue
                if text[i] == "'":
                    if i + 1 < n and text[i + 1] == "'":
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            else:
                raise ScanError("unterminated string literal")
            out.append(" 'STR' ")
            in_ident = False
        elif ch == '"':                        # quoted identifier
            i += 1
            while i < n:
                if text[i] == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            else:
                raise ScanError("unterminated quoted identifier")
            out.append(" 'QID' ")
            in_ident = False
        elif ch == "$":                        # dollar-quoted string ($tag$...$tag$)
            # SEV-1: inside an identifier a '$' NEVER opens a dollar-quote
            # ('b$$c' is ONE identifier to PG — the phantom-quote P0)
            if in_ident:
                out.append(ch)
                i += 1
                continue
            m = DOLLAR_OPEN_RE.match(text, i)
            if m:
                tag = m.group(0)
                end = text.find(tag, m.end())
                if end == -1:
                    raise ScanError("unterminated dollar-quoted string")
                i = end + len(tag)
                out.append(" 'DQ' ")
                in_ident = False
            else:
                out.append(ch)
                i += 1
        else:
            out.append(ch)
            if _ident_start(ch):
                in_ident = True
            elif in_ident and _ident_cont(ch):
                pass
            else:
                in_ident = False
            i += 1
    return "".join(out)


def _statement_heads(masked: str):
    """Yield the word-token head of each top-level statement (';' is safe to
    split on: every literal/comment/quote body is already a placeholder)."""
    for stmt in masked.split(";"):
        words = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", stmt)
        if words:
            yield [w.upper() for w in words]


def _classify(masked: str) -> str:
    """Classify a file's executable text against the admitted grammar.
    Returns 'ok' or the first violation's description (fail-closed)."""
    for stmt in masked.split(";"):
        words = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", stmt)
        if not words:
            continue
        w = [x.upper() for x in words]
        if w[0] == "GRANT" or w[0] == "COMMENT" or (w[0] == "SET" and len(w) > 1
                and w[1] not in ("TRANSACTION", "SESSION")):
            continue
        if w[0] == "ALTER" and len(w) > 1 and w[1] == "TABLE":
            continue  # ALTER TABLE x DROP is the destructive set's own case (ARV-MIG-003)
        if w[0] == "DROP" and len(w) > 2 and w[1] in _DROP_IFEXISTS and w[2] == "IF" and "EXISTS" in w:
            continue  # the idempotent-recreate pattern the substrate migrations use
        if w[0] == "CREATE":
            body = [x for x in w[1:] if x not in _CREATE_SKIP]
            kind = body[0] if body else ""
            if kind == "INDEX" and "CONCURRENTLY" in w:
                return "construct (CREATE INDEX CONCURRENTLY — cannot run inside the runner's single transaction)"
            if kind in _PLAIN_CREATE:
                # SEV-3: an admitted head's BODY may still carry a data-modifying
                # CTE — migrations declare schema, never queries
                if DATA_MODIFY_RE.search(stmt):
                    return "data-modifying statement inside an admitted head (the grammar admits schema, never queries)"
                continue
            return f"procedural/dynamic construct (CREATE {kind or '?'}) the grammar cannot classify"
        if w[0] in ("DO", "EXECUTE", "CALL", "PREPARE", "DEALLOCATE", "COPY",
                    "INSERT", "UPDATE", "MERGE", "SELECT", "WITH", "VALUES",
                    "REVOKE", "ANALYZE", "VACUUM", "REINDEX", "REFRESH", "TRUNCATE",
                    "LOCK", "LISTEN", "NOTIFY", "LOAD", "IMPORT", "SECURITY"):
            if w[0] == "SELECT":
                return "unclassified construct (SELECT) — migrations declare schema, not queries"
            return f"procedural/dynamic or data construct ({w[0]}) the grammar cannot classify"
        return f"unclassified construct ({w[0]}) the grammar cannot classify"
    return "ok"


def _statement_tokens(masked: str):
    """Yield the word-token list of each top-level statement (';' is safe to
    split on: every literal/comment/quote body is already a placeholder)."""
    for stmt in masked.split(";"):
        words = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", stmt)
        if words:
            yield [w.upper() for w in words]


def _txn_control_head(w: list) -> bool:
    """Transaction control at STATEMENT-HEAD level (the #82 Major): a bare END
    (PG's COMMIT synonym — live under the runner's prepended BEGIN) is control
    when it HEADS a statement; CASE's mid-statement END never does. START/SET/
    PREPARE count only in their transaction forms (a config SET stays admitted)."""
    if not w:
        return False
    if w[0] in ("BEGIN", "COMMIT", "ROLLBACK", "SAVEPOINT", "ABORT", "END"):
        return True
    if w[0] == "START" and len(w) > 1 and w[1] == "TRANSACTION":
        return True
    if w[0] == "SET" and len(w) > 1 and w[1] in ("TRANSACTION", "SESSION"):
        return True
    if w[0] == "PREPARE" and len(w) > 1 and w[1] == "TRANSACTION":
        return True
    if w[0] in ("COMMIT", "ROLLBACK") and len(w) > 1 and w[1] == "PREPARED":
        return True
    return False


def _alter_drop(w: list) -> bool:
    """Any DROP action inside an ALTER TABLE statement is destructive-class,
    whatever tokens precede it (the #82 Major: the one-token regex missed
    ONLY/ADD-then-DROP/QID-object/spaced-dot forms). Exact-token matching — a
    name merely containing 'drop' never fires (quoted identifiers are masked)."""
    return len(w) > 2 and w[0] == "ALTER" and w[1] == "TABLE" and "DROP" in w[2:]


def oracle(v: int, name: str, text: str, has_directive: bool) -> None:
    """The M0 oracle: refuses, BEFORE any execution, what the runner cannot
    prove transaction-safe. Zero effects are structural from here on."""
    try:
        masked = mask(text)
    except ScanError as e:
        _die("ARV-MIG-016",
             f"migration {v:04d}_{name} cannot be scanned fail-closed ({e})",
             "repair the SQL so every string/comment/quote terminates — an untrustworthy mask never scans")
    tokens = list(_statement_tokens(masked))
    for w in tokens:
        if _txn_control_head(w):
            _die("ARV-MIG-011",
                 f"migration {v:04d}_{name} contains embedded transaction control (statement head '{w[0]}')",
                 "the runner owns the ONE transaction boundary — remove BEGIN/COMMIT/END/ROLLBACK/SAVEPOINT/"
                 "PREPARE TRANSACTION from the file; a mid-file commit (END included — PG's own COMMIT synonym) "
                 "would persist partial effects while the runner reports a rollback")
    destructive = bool(DESTRUCTIVE_RE.search(masked)) or any(_alter_drop(w) for w in tokens)
    if destructive and not has_directive:
        _die("ARV-MIG-003",
             f"migration {v:04d}_{name} contains a destructive statement without an explicit baseline bump",
             "destructive operations require a '-- arv-baseline-bump: <n>' directive line in the file (the owner-visible paper trail)")
    verdict = _classify(masked)
    baseline_exempt = (v == 1 and name == "baseline")  # the DECLARED, name-scoped bootstrap exemption
    if verdict != "ok" and not has_directive and not baseline_exempt:
        _die("ARV-MIG-015",
             f"migration {v:04d}_{name} is refused by the admitted grammar: {verdict}",
             "the fail-closed grammar admits only what it can classify; procedural/dynamic constructs require a "
             "'-- arv-baseline-bump: <n>' directive line (the owner-visible paper trail) — or narrow the file to the admitted grammar")


def discover(mdir: str) -> list:
    out = []
    for name in sorted(os.listdir(mdir)):
        m = SAFE_NAME_RE.match(name)
        if not m:
            _die("ARV-MIG-014", f"migration filename outside the safe alphabet: {name!r}",
                 "migration files are NNNN_name.sql, the name lowercase letters/digits/underscores "
                 "only (first char a letter) — the alphabet makes the ledger INSERT's literal provably "
                 "safe (F-010); quotes/dashes/case never reach the bookkeeping INSERT")
        out.append((int(m.group(1)), m.group(2), os.path.join(mdir, name)))
    return out


def _parse_ledger(r) -> dict:
    """{version: (name, checksum)}. Fail-closed (the #82 round): an unparseable
    row (a '|' smuggled into name/checksum) is a NAMED ARV-MIG-007 refusal —
    never a silently dropped row hiding a poisoned ledger from both paths."""
    rows = {}
    for line in r.out.splitlines():
        parts = line.split("|")
        if len(parts) == 3 and parts[0].lstrip("-").isdigit():
            rows[int(parts[0])] = (parts[1], parts[2])
        elif line.strip():
            _die("ARV-MIG-007",
                 f"the bookkeeping table carries an unparseable row ({line.strip()[:60]!r}) — a poisoned ledger",
                 "every ledger row must parse (version|name|checksum); a row that does not is a named refusal, never "
                 "silently dropped — reconcile the ledger with the history (never edit it by hand)")
    return rows


def applied(db: str, bootstrap: bool = True) -> dict:
    """The ledger read: {version: (name, checksum)} (SEV-5: the bidirectional
    check compares NAMES too, never versions+checksums alone)."""
    if bootstrap:  # the WRITE path's bootstrap: the migrator creates the ledger
        pg.psql(
            "CREATE SCHEMA IF NOT EXISTS arv; "
            "CREATE TABLE IF NOT EXISTS arv.schema_migrations ("
            "version BIGINT PRIMARY KEY, name TEXT NOT NULL, checksum TEXT NOT NULL, "
            "applied_at TIMESTAMPTZ NOT NULL DEFAULT now(), applied_by TEXT NOT NULL);",
            db=db,
        )
    r = pg.psql("SELECT version, name, checksum FROM arv.schema_migrations ORDER BY version;", db=db)
    if r.returncode != 0:
        if not bootstrap and "does not exist" in r.stderr:
            _die("ARV-MIG-013",
                 "--verify is observation-only: the bookkeeping table does not exist (this DB was never migrated)",
                 "run migrate first — verify never fabricates the ledger it claims to observe "
                 "(no CREATE under a claimed read-only pass)")
        _die("ARV-MIG-007", "cannot read the migrations bookkeeping table",
             f"the rig's DB must be reachable and arv.schema_migrations readable: {r.stderr.strip()[:200]}")
    return _parse_ledger(r)


def _ledger_opt(db: str):
    """The pre-scan's observation-only read (SEV-7): None when the table does
    not exist (never-migrated — every file pending); any failure other than
    the positive absence fails closed here."""
    r = pg.psql("SELECT version, name, checksum FROM arv.schema_migrations ORDER BY version;", db=db)
    if r.returncode != 0:
        if "does not exist" in r.stderr:
            return None
        _die("ARV-MIG-007", "cannot read the migrations bookkeeping table",
             f"the rig's DB must be reachable and arv.schema_migrations readable: {r.stderr.strip()[:200]}")
    return _parse_ledger(r)


def _check_bidirectional(db: str, files: list, done: dict) -> None:
    """History consistency, BOTH ways (ARV-MIG-012): extra rows; interior holes
    (the applied set must be a contiguous prefix — a hand-deleted middle row
    would silently re-apply an old file out of order); name drift (a renamed
    applied file)."""
    versions = [v for v, _, _ in files]
    names = {v: nm for v, nm, _ in files}
    extra = sorted(set(done) - set(versions))
    if extra:
        _die("ARV-MIG-012",
             f"the migration history is inconsistent BOTH ways: ledger rows the directory cannot account for: {extra}",
             "every ledger row must correspond to a directory file — an applied version missing from the directory "
             "(or smuggled into the ledger) is a broken history: reconcile the directory and the ledger "
             "(never edit the ledger by hand; re-derive it)")
    applied_versions = sorted(done)
    if applied_versions and applied_versions != list(range(1, len(applied_versions) + 1)):
        _die("ARV-MIG-012",
             f"the applied ledger has an INTERIOR HOLE: applied versions {applied_versions} "
             "are not a contiguous prefix of the directory",
             "the applied set must be 1..k contiguous — a hole means a hand-edited ledger and would "
             "silently re-apply an old file out of order; reconcile the ledger with the history (never edit it by hand)")
    for v, (ledger_name, _) in done.items():
        if v in names and ledger_name != names[v]:
            _die("ARV-MIG-012",
                 f"the ledger row for version {v} carries name '{ledger_name}' but the directory file is "
                 f"'{names[v]}' — a renamed applied file",
                 "an applied file's identity is its version AND name — rename the file back or re-derive "
                 "the ledger; a renamed applied file must never pass silently")


def run(db: str, mdir: str) -> int:
    files = discover(mdir)
    if not files:
        _die("ARV-MIG-008", f"no migrations found in {mdir}", "S1 ships 0001_baseline.sql — the directory cannot be empty")
    versions = [v for v, _, _ in files]
    if versions[0] != 1 or versions != list(range(1, len(versions) + 1)):
        _die("ARV-MIG-004", f"the version set is not a gapless sequence from the baseline: {versions}",
             "migrations are forward-only from 0001; renumber the directory (no holes, no recycling)")
    # SEV-7: the pre-scan BEFORE the first DB write — a refusal leaves the DB untouched.
    done_opt = _ledger_opt(db)
    pending = [f for f in files if done_opt is None or f[0] not in done_opt]
    for v, name, path in pending:
        blob = open(path, "rb").read()
        text = blob.decode("utf-8", "replace")
        # The oracle runs BEFORE psql: a refusal is structurally effect-free.
        oracle(v, name, text, bool(BUMP_RE.search(text)))
    done = applied(db)  # the WRITE path's first DB write — after every pending file passed the oracle
    _check_bidirectional(db, files, done)
    applied_any = False
    for v, name, path in files:
        blob = open(path, "rb").read()
        digest = hashlib.sha256(blob).hexdigest()
        if v in done:
            if done[v][1] != digest:
                _die("ARV-MIG-005", f"applied migration {v:04d}_{name} was EDITED after apply (recorded checksum differs)",
                     "an applied migration is immutable history — revert the file edit or add a new migration")
            continue  # already applied, unchanged: the no-op path
        text = blob.decode("utf-8", "replace")
        # ONE transaction: the migration AND its bookkeeping row commit together
        # (argv-travelled -c, no shell; the alphabet makes {name} provably safe).
        stmt = (
            "BEGIN;\n" + text +
            f"\nINSERT INTO arv.schema_migrations (version, name, checksum, applied_by) "
            f"VALUES ({v}, '{name}', '{digest}', 'harness/migrate.py');\nCOMMIT;"
        )
        r = pg.psql(stmt, db=db)
        if r.returncode != 0:
            _die("ARV-MIG-009", f"migration {v:04d}_{name} failed and was rolled back",
                 f"fix the SQL; the DB is unchanged (transaction proof): {r.stderr.strip()[:300]}")
        print(f"applied {v:04d}_{name}")
        applied_any = True
    if not applied_any:
        print("ARV-MIG-001: nothing to apply — no-op (all recorded, unchanged)")
    return 0


def verify(db: str, mdir: str) -> int:
    files = discover(mdir)
    done = applied(db, bootstrap=False)  # ARV-MIG-013: verify creates NOTHING
    _check_bidirectional(db, files, done)
    bad = []
    for v, name, path in files:
        digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if v not in done:
            bad.append(f"{v:04d}_{name}: not applied")
        elif done[v][1] != digest:
            bad.append(f"{v:04d}_{name}: checksum drift (edited after apply)")
    if bad:
        _die("ARV-MIG-010", f"verify failed: {'; '.join(bad)}", "run migrate; never edit an applied file (ARV-MIG-005)")
    print(f"verify OK: {len(files)} migration(s) applied, checksums match")
    return 0


def main() -> int:
    cfg = pg.config()
    db = os.environ.get("PGDATABASE", "postgres")
    mdir = cfg["ARV_MIGRATIONS_DIR"]
    if "--verify" in sys.argv:
        return verify(db, mdir)
    # No pre-count bootstrap (the zero-effects contract): discovery, the
    # sequence check and the alphabet all fire before the first DB touch in run().
    return run(db, mdir)


if __name__ == "__main__":
    sys.exit(main())
