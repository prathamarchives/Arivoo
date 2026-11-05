#!/usr/bin/env python3
"""harness/tests/test_contract.py — P4-00a acceptance suite (CLAIM-062, the
truthful-acknowledgment contract + the user-facing entry; PLAN's elaborated
P4-00a card; the Phase 3 exit gate's routed register, record 53 §5).
Red-first (LAW-11): at CLAIM-061's merged head b1a4934 the suite fails with
ARV-TEST-000 (machinery-absent; red-01.txt) — every routed repair is absent.

THE CONTRACT: the product's user-facing surface tells the whole truth at
every acknowledgment and entry point — SYS-01's every-write rule extends to
the import/extract acks (the durability rung named, never implied); the
restore's typed completion names the derived-rebuild step (RTM §3.7's
restored -> fully_operational ladder made visible — the acceptance run's
silent-search-miss class dead); get-capture exposes the anchor_id (the
observability the grader corrected — get-history always had it); the search
output labels its columns; migrate.py --help prints help and NEVER executes
(a help request is not a migration command); the user-facing README at the
repo root carries the day-one path (the connection env INCLUDING PGDATABASE,
the workflow verbs, the durability vocabulary) — the surface the uncoached
acceptance agent had to assemble from --help and the engineering records.

Cases (the CON registry; each pin's full statement lives at its check()):
  CON-01 the import ack truthfulness: the committed AND the replayed acks
         carry durability_rung=local_durable (SYS-01's every-write rule)
  CON-02 the extract ack truthfulness: the committed AND the replayed acks
         carry durability_rung=local_durable
  CON-03 the restore completion names the derived-rebuild step: the RESTORED
         line carries state=restored derived_state=pending_rebuild and the
         rebuild verbs (never the silent derived miss)
  CON-04 get-capture exposes the anchor_id — and it is the REAL anchor (the
         resolve-anchor arm answers resolved on it)
  CON-05 the search output labels its columns (the header line precedes the
         rows; the rows still parse kind|entity_id|revision|matched_terms)
  CON-06 migrate.py --help prints usage and exits 0 WITHOUT executing (a
         clean database keeps zero arv tables after a help request); the
         --verify arm still works
  CON-07 the user-facing README at the repo root: the connection env
         (PGHOST/PGPORT/PGUSER/PGDATABASE), the day-one workflow verbs
         (import, highlight, bookmark, note, search, export, restore), and
         the durability vocabulary (durability_rung)

Run: python3 harness/tests/test_contract.py   (exit 0 = green)
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from harness.adapters import pg  # noqa: E402

FAILS: list[str] = []

# the machinery-absent probe (the RED gate): the routed repairs are ABSENT at
# the RED tree — README.md missing at the root OR the migrate --help misfire
# (help EXECUTES the migration) is the cheapest honest probe pair (LAW-11;
# the EXP/SYN precedent form). The probe's migrate call runs against a
# THROWAWAY scratch DB — at the RED tree --help executes, and the probe must
# observe that WITHOUT side effects on any shared database.
_readme = REPO / "README.md"
_probe_db = pg.create_scratch_db("p400aprobe")
try:
    _help = subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py"), "--help"],
                           capture_output=True, text=True, timeout=120,
                           env=dict(os.environ, PGDATABASE=_probe_db))
    _help_broken = not (_help.returncode == 0 and "usage" in (_help.stdout + _help.stderr).lower())
finally:
    pg.drop_scratch_db(_probe_db)
if not _readme.is_file() or _help_broken:
    print(f"FAIL ARV-TEST-000: the P4-00a truthful-surface machinery is absent "
          f"(machinery-absent class; README at root: {_readme.is_file()}; "
          f"migrate --help answers usage without executing: {not _help_broken}) "
          "— the implementation lands after this RED, never before it (LAW-11)")
    sys.exit(1)

SRC = DST = None
ENV = None

TEXT = ("The contract corpus: the quiet harbor rides here.\n"
        "A second line with the capture window inside.\n")


def check(code: str, ok: bool, what: str, repair: str) -> None:
    if ok:
        print(f"PASS {code}: {what}")
    else:
        print(f"FAIL {code}: {what}")
        print(f"      repair: {repair}")
        FAILS.append(code)


def cli(*args, env=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          timeout=300, env=env or ENV)


def cmd(op: str, *args, owner="A", key=None, env=None) -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "commands.py"), op, "--owner", owner,
         "--actor", "owner", "--client-id", "cli-1"]
    if key is not None:
        a += ["--idem-key", key]
    return cli(*a, *args, env=env)


def query(*args, env=None) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "query.py"), *args, env=env or ENV)


def export(*args, env=None) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "export.py"), *args, env=env or ENV)


def main() -> int:
    global SRC, DST, ENV
    SRC = pg.create_scratch_db("p400a")
    DST = pg.create_scratch_db("p400adst")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=SRC, ARV_BLOB_DIR=blob_dir)
    try:
        for db in (SRC, DST):
            subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                           capture_output=True, text=True, timeout=180,
                           env=dict(ENV, PGDATABASE=db), check=True)

        # the fixture: import + extract + the capture families (owner A)
        src_file = pathlib.Path(tempfile.mkdtemp(prefix="arv-p400a-")) / "corpus.md"
        src_file.write_text(TEXT, encoding="utf-8")
        r_imp = cmd("import_source", "--title", "The Contract Corpus",
                    "--file", str(src_file), key="imp-1")
        sid = ""
        for ln in r_imp.stdout.splitlines():
            if ln.startswith("ACK") and "result_ref=" in ln:
                sid = ln.split("result_ref=")[1].split()[0]
        r_ext = cmd("extract_source", "--source-id", sid, key="ext-1")
        r_hl = cmd("create_highlight", "--source-id", sid, "--start", 0,
                   "--end", 30, key="hl-1")
        hid = ""
        for ln in r_hl.stdout.splitlines():
            if ln.startswith("ACK") and "result_ref=" in ln:
                hid = ln.split("result_ref=")[1].split()[0]
        cmd("create_bookmark", "--source-id", sid, "--start", 0, "--end", 10,
            key="bm-1")
        cmd("create_note", "--content", "the quiet harbor note",
            "--ref", f"highlight:{hid}@1", key="nt-1")

        # ---- CON-01 — the import ack truthfulness
        r_replay = cmd("import_source", "--title", "The Contract Corpus",
                       "--file", str(src_file), key="imp-1")
        ok1 = (r_imp.returncode == 0 and r_replay.returncode == 0
               and "durability_rung=local_durable" in r_imp.stdout
               and "durability_rung=local_durable" in r_replay.stdout)
        check("CON-01", ok1,
              "the import ack names its durability rung on BOTH forms — the committed ack and the replayed ack carry durability_rung=local_durable (SYS-01's every-write rule: an acknowledged capture never leaves its persistence state implied; the uncoached acceptance run's finding answered)",
              "commands.py's import arms: append durability_rung=local_durable to the committed extra and the replayed ack line — the same vocabulary the capture/bookmark/note families already carry")

        # ---- CON-02 — the extract ack truthfulness
        r_ext2 = cmd("extract_source", "--source-id", sid, key="ext-1")
        ok2 = (r_ext.returncode == 0 and r_ext2.returncode == 0
               and "durability_rung=local_durable" in r_ext.stdout
               and "durability_rung=local_durable" in r_ext2.stdout)
        check("CON-02", ok2,
              "the extract ack names its durability rung on BOTH forms — the generation's committed and replayed acks carry durability_rung=local_durable (the derived layer is still a committed local write; an ack that omits the rung underclaims)",
              "extract.py: append durability_rung=local_durable to both ack lines")

        # ---- CON-05 — the search output labels its columns
        r_search = query("search", "--owner", "A", "quiet")
        first = next((ln for ln in r_search.stdout.splitlines() if ln.strip()), "")
        rows = [ln for ln in r_search.stdout.splitlines()
                if ln.strip() and not ln.startswith("#")]
        ok5 = (r_search.returncode == 0
               and first.startswith("#") and "kind" in first and "entity_id" in first
               and any(ln.startswith("source|") for ln in rows)
               and any(ln.startswith("note|") for ln in rows))
        check("CON-05", ok5,
              "the search output labels its columns: a header line (kind|entity_id|revision|matched_terms) precedes the result rows — the user never guesses what the pipes mean (the acceptance run's 'unlabeled search output' finding answered; the row shape unchanged, the existing suites' assertions unaffected)",
              "query.py's search arm: print the header line before the rows")

        # ---- CON-04 — get-capture exposes the anchor_id
        r_cap = query("get-capture", "--owner", "A", "--id", hid)
        cap = {}
        try:
            cap = json.loads(r_cap.stdout.strip().splitlines()[0])
        except (ValueError, IndexError):
            pass
        anchor_id = cap.get("anchor_id", "")
        r_res = query("resolve-anchor", "--owner", "A", "--id", anchor_id) if anchor_id else None
        ok4 = (r_cap.returncode == 0 and bool(anchor_id)
               and r_res is not None and r_res.returncode == 0
               and '"resolved"' in r_res.stdout)
        check("CON-04", ok4,
              "get-capture exposes the anchor_id — and it is the REAL anchor: the resolve-anchor arm answers resolved on exactly that id (the observability the grader corrected: get-history always had it, the ordinary read now does too — a user can diagnose an anchor without the history arm)",
              "query.py's CAP_SQL: add a.id AS anchor_id to the projected columns")

        # ---- CON-03 — the restore completion names the derived-rebuild step
        arch = pathlib.Path(tempfile.mkdtemp(prefix="arv-arch-")) / "lib"
        r_exp = export("export", "--owner", "A", "--out", str(arch))
        dst_env = dict(ENV, PGDATABASE=DST)
        r_res2 = export("restore", "--archive", str(arch), env=dst_env)
        ok3 = (r_exp.returncode == 0 and r_res2.returncode == 0
               and "derived_state=pending_rebuild" in r_res2.stdout
               and "state=restored" in r_res2.stdout
               and "rebuild_keyword_index" in r_res2.stdout)
        check("CON-03", ok3,
              "the restore's typed completion names the derived-rebuild step: the RESTORED line carries state=restored derived_state=pending_rebuild and the rebuild verbs (extract_source + rebuild_keyword_index) — RTM §3.7's restored -> fully_operational ladder made VISIBLE at the one moment the step is needed (the acceptance run's silent-search-miss class dead: the user is TOLD the derived layer awaits rebuild, never left to discover an empty search)",
              "export.py's completion line: append state=restored derived_state=pending_rebuild rebuild=extract_source+rebuild_keyword_index")

        # ---- CON-06 — migrate.py --help prints help and NEVER executes
        clean = pg.create_scratch_db("p400ahelp")
        try:
            r_h = cli(str(REPO / "harness" / "migrate.py"), "--help",
                      env=dict(ENV, PGDATABASE=clean))
            r_v = cli(str(REPO / "harness" / "migrate.py"), "--verify",
                      env=dict(ENV, PGDATABASE=SRC))
            probe = subprocess.run(["psql", "-X", "-A", "-t", "-U", "arv_read", "-d", clean,
                                    "-c", "SELECT count(*) FROM pg_tables WHERE schemaname='arv'"],
                                   capture_output=True, text=True, timeout=60, env=ENV)
            n_arv = probe.stdout.strip()
        finally:
            pg.drop_scratch_db(clean)
        ok6 = (r_h.returncode == 0
               and "usage" in (r_h.stdout + r_h.stderr).lower()
               and "--verify" in (r_h.stdout + r_h.stderr)
               and n_arv == "0"
               and r_v.returncode == 0)
        check("CON-06", ok6,
              "migrate.py --help prints usage and exits 0 WITHOUT executing — a clean database keeps ZERO arv tables after a help request (the acceptance run's 'migrate.py --help executes instead of helping' misfire dead); the --verify arm still works",
              "migrate.py: argparse with --help (the default) and --verify flags; the default action unchanged (the apply path)")

        # ---- CON-07 — the user-facing README at the repo root
        readme = _readme.read_text(encoding="utf-8") if _readme.is_file() else ""
        rl = readme.lower()
        ok7 = (_readme.is_file() and len(readme) > 400
               and all(t in rl for t in ("pghost", "pgport", "pguser", "pgdatabase"))
               and all(v in rl for v in ("import", "highlight", "bookmark", "note",
                                          "search", "export", "restore"))
               and "durability_rung" in rl)
        check("CON-07", ok7,
              "the user-facing README at the repo root: the connection env INCLUDING PGDATABASE (the undocumented default the acceptance agent tripped on), the day-one workflow verbs (import, highlight, bookmark, note, search, export, restore), and the durability vocabulary (durability_rung) — the entry surface the uncoached agent had to assemble from --help and the engineering records",
              "write README.md at the repo root: the day-one path (setup, the connection env, the workflow, the durability vocabulary)")

        print()
        if FAILS:
            print(f"RED — {len(FAILS)} failure(s): {', '.join(FAILS)}")
            return 1
        print("GREEN — the truthful-acknowledgment contract + the user-facing entry hold "
              "(CON-01..07; the Phase 3 exit gate's routed register answered)")
        return 0
    finally:
        if SRC:
            pg.drop_scratch_db(SRC)
        if DST:
            pg.drop_scratch_db(DST)


if __name__ == "__main__":
    sys.exit(main())
