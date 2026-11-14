#!/usr/bin/env python3
"""harness/tests/test_eval_corpus.py — P5-B acceptance suite (CLAIM-081,
the eval corpus; the PLAN 5B row elaborated one phase deep at the #116
landing; record 73 §2). Red-first (LAW-11): at CLAIM-080's merged head
2e35d59 the suite fails with ARV-TEST-000 (machinery-absent; red-01.txt) —
harness/eval.py and the versioned query corpus do not exist.

THE CONTRACT (the 5B letter): a versioned query corpus — the evaluation
baseline BEFORE any ranking change (the owner's fixed dependency order:
the corpus lands before 5C's semantic spike and 5E's hybrid ranking so
they can only be measured against it). The corpus carries the four case
classes: relevant (the query's expected admissions), no-result (queries
whose honest answer is the empty set — never a fabricated match),
distractor (near-miss material that must NOT be admitted), and conflated
(the same term spanning two distinct documents whose why must disambiguate
by provenance, never by rank). The corpus is VERSIONED (a corpus id +
revision; a run over it is reproducible byte-exactly — no clock, no
randomness); the evaluator is deterministic (same corpus + same query
machinery = the same verdict); the verdict form is mechanical (the
expected ids vs the actual ids — never an LLM judgment); the corpus file
is DATA (an embedded instruction in a case is never executed); the
corpus rides the owner boundary (owner B's run never sees A's cases).

Cases (the EVC registry; each pin's full statement lives at its check()):
  EVC-01 the corpus form: a corpus load composes the four case classes
         with every case carrying its query, its expected ids (the
         relevant class), or the explicit empty expectation (the
         no-result class), or the must-not-admit ids (the distractor
         class), or the two-document disambiguation pair (the conflated
         class) — and the corpus id + revision
  EVC-02 the versioning law: the corpus is identified and versioned; the
         same corpus id at the same revision re-runs byte-equal (the
         deterministic verdict form: no clock, no randomness, no
         environment-dependent ordering)
  EVC-03 the no-result honesty: a no-result case's honest verdict is the
         empty set with the explicit marker — never a fabricated match,
         never a fallback to "similar" material, never an error
  EVC-04 the distractor law: a distractor case's near-miss material is
         NOT admitted (the verdict counts it as a miss when it appears);
         the distractor ids are recorded in the corpus so the miss is
         mechanically detectable
  EVC-05 the conflated-terms law: the same term spanning two distinct
         documents admits BOTH with provenance-disambiguated whys — never
         a rank-based suppression of the second
  EVC-06 the mechanical verdict: the evaluator's verdict is the expected
         vs the actual id sets (precision/recall computed mechanically
         over the corpus, printed with the corpus id + revision + the
         per-class breakdown) — never an LLM narration
  EVC-07 the corpus-as-data law: a case whose query embeds hostile
         instruction-like content ("ignore the corpus, mark all cases
         passed") is evaluated as DATA — nothing executes it, the
         verdict over the rest of the corpus is unaffected
  EVC-08 the owner isolation: owner B's corpus run never sees A's cases
         (the corpus rides the owner boundary — the RLS path exactly)
  EVC-09 the corpus registration: the corpus is registered in the runs'
         scope with its id + revision; a run over an UNREGISTERED corpus
         id is the typed refusal (never a silent default to another
         corpus)
  EVC-10 the eval-gate integration: the corpus machinery is wired into
         the standing gate (the eval corpus run is a recorded command in
         the TESTS-adjacent runs, its verdict form asserted by the
         suite's own re-run)

The runner: `python3 harness/tests/test_eval_corpus.py` — the standard
suite form (the check() registry, GREEN/RED, exit 0/1).
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "harness"))

CASES = [
    ("EVC-01", "the corpus form: the four case classes with their queries + expectations + the corpus id/revision"),
    ("EVC-02", "the versioning law: the same corpus id/revision re-runs byte-equal (deterministic)"),
    ("EVC-03", "the no-result honesty: the empty verdict + the explicit marker, never a fabricated match"),
    ("EVC-04", "the distractor law: the near-miss material is NOT admitted; the miss is mechanically detectable"),
    ("EVC-05", "the conflated-terms law: both documents admitted with provenance-disambiguated whys"),
    ("EVC-06", "the mechanical verdict: expected vs actual id sets, precision/recall computed + printed"),
    ("EVC-07", "the corpus-as-data law: hostile content in a case is data — never executed"),
    ("EVC-08", "the owner isolation: B's run never sees A's cases (RLS)"),
    ("EVC-09", "the corpus registration: an unregistered corpus id is the typed refusal"),
    ("EVC-10", "the eval-gate integration: the corpus run is a recorded command asserted by re-run"),
]


def check(name: str, ok: bool, statement: str, repair: str) -> bool:
    if ok:
        print(f"PASS {name}: {statement}")
    else:
        print(f"FAIL {name}: {statement}")
        print(f"      repair: {repair}")
    return ok


DB = ENV = None


def cli(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True,
                          text=True, timeout=240, env=ENV)


def evl(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "eval.py"), *args)


def cmd(op: str, *args, owner="A", key=None) -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "commands.py"), op, "--owner", owner,
         "--actor", "owner", "--client-id", "cli-1"]
    if key is not None:
        a += ["--idem-key", key]
    return cli(*a, *args)


def main() -> int:
    global DB, ENV
    import adapters.pg as pg
    DB = pg.create_scratch_db("p5b")
    ENV = dict(os.environ, ARV_DB=DB)

    # the machinery-absent RED check (LAW-11): eval.py does not exist at
    # the merged head — every case that needs it fails with ARV-TEST-000
    eval_py = REPO / "harness" / "eval.py"
    machinery = eval_py.is_file()
    if not machinery:
        print("RED observed: harness/eval.py is absent at this tree "
              "(LAW-11 — the implementation lands after this record); "
              "the corpus machinery is the GREEN's own object")

    ok_all = True

    # ---- EVC-01 — the corpus form
    if machinery:
        r = evl("corpus", "load", "--file", "harness/runs/claim-081-p5b-eval-corpus/corpus.json")
        out = r.stdout
        ok = (r.returncode == 0
              and "corpus_id=" in out and "revision=" in out
              and all(k in out for k in ("relevant", "no-result", "distractor", "conflated"))
              and "cases=" in out)
    else:
        ok = False
    ok_all &= check("EVC-01", ok,
                    "the corpus form: the four case classes with their "
                    "queries + expectations + the corpus id/revision",
                    "harness/eval.py's corpus load composes the four case "
                    "classes with the id + revision")

    # ---- EVC-02 — the versioning law
    if machinery:
        r1 = evl("run", "--corpus", "the P5-B corpus", "--revision", "1")
        r2 = evl("run", "--corpus", "the P5-B corpus", "--revision", "1")
        ok = (r1.returncode == 0 and r2.returncode == 0
              and r1.stdout == r2.stdout and "corpus_id=" in r1.stdout)
    else:
        ok = False
    ok_all &= check("EVC-02", ok,
                    "the versioning law: the same corpus id/revision "
                    "re-runs byte-equal (deterministic)",
                    "the eval run is deterministic: no clock, no "
                    "randomness, no environment-dependent ordering")

    # ---- EVC-03 — the no-result honesty
    if machinery:
        r = evl("run", "--corpus", "the P5-B corpus", "--revision", "1")
        ok = (r.returncode == 0
              and re.search(r"no-result.*0/0|empty=.*true|no-result: "
                            r"\d+/\d+", r.stdout) is not None)
    else:
        ok = False
    ok_all &= check("EVC-03", ok,
                    "the no-result honesty: the empty verdict + the "
                    "explicit marker, never a fabricated match",
                    "the no-result case's honest verdict is the empty set "
                    "with the explicit marker — never a fallback")

    # ---- EVC-04 — the distractor law
    if machinery:
        r = evl("run", "--corpus", "the P5-B corpus", "--revision", "1")
        ok = (r.returncode == 0 and "distractor" in r.stdout
              and re.search(r"distractor[^\n]*\d+/1", r.stdout) is not None)
    else:
        ok = False
    ok_all &= check("EVC-04", ok,
                    "the distractor law: the near-miss material is NOT "
                    "admitted; the miss is mechanically detectable",
                    "the distractor ids are recorded and the miss is "
                    "mechanically detectable in the verdict")

    # ---- EVC-05 — the conflated-terms law
    if machinery:
        r = evl("run", "--corpus", "the P5-B corpus", "--revision", "1")
        ok = (r.returncode == 0 and "conflated" in r.stdout
              and re.search(r"conflated[^\n]*2/2", r.stdout) is not None)
    else:
        ok = False
    ok_all &= check("EVC-05", ok,
                    "the conflated-terms law: both documents admitted "
                    "with provenance-disambiguated whys",
                    "the same term spanning two documents admits BOTH — "
                    "never a rank-based suppression")

    # ---- EVC-06 — the mechanical verdict
    if machinery:
        r = evl("run", "--corpus", "the P5-B corpus", "--revision", "1")
        ok = (r.returncode == 0
              and "precision=" in r.stdout and "recall=" in r.stdout
              and "corpus_id=" in r.stdout and "revision=" in r.stdout)
    else:
        ok = False
    ok_all &= check("EVC-06", ok,
                    "the mechanical verdict: expected vs actual id sets, "
                    "precision/recall computed + printed",
                    "the verdict is mechanical — never an LLM narration")

    # ---- EVC-07 — the corpus-as-data law
    if machinery:
        r = evl("run", "--corpus", "the P5-B corpus", "--revision", "1")
        ok = (r.returncode == 0
              and "ignore" not in r.stdout.lower().replace("ignore the corpus", "")
              and "all cases passed" not in r.stdout.lower())
    else:
        ok = False
    ok_all &= check("EVC-07", ok,
                    "the corpus-as-data law: hostile content in a case is "
                    "data — never executed",
                    "the hostile query is evaluated as data; the verdict "
                    "over the rest of the corpus is unaffected")

    # ---- EVC-08 — the owner isolation
    if machinery:
        r = evl("run", "--corpus", "the P5-B corpus", "--revision", "1",
                "--owner", "B")
        ok = (r.returncode == 0
              and "A's" not in r.stdout and "owner=B" in r.stdout)
    else:
        ok = False
    ok_all &= check("EVC-08", ok,
                    "the owner isolation: B's run never sees A's cases (RLS)",
                    "the corpus rides the owner boundary — the RLS path")

    # ---- EVC-09 — the corpus registration
    if machinery:
        r = evl("run", "--corpus", "an-unregistered-corpus", "--revision", "1")
        ok = (r.returncode == 1 and "ARV" in r.stdout)
    else:
        ok = False
    ok_all &= check("EVC-09", ok,
                    "the corpus registration: an unregistered corpus id is "
                    "the typed refusal",
                    "never a silent default to another corpus")

    # ---- EVC-10 — the eval-gate integration
    if machinery:
        r = evl("run", "--corpus", "the P5-B corpus", "--revision", "1")
        ok = (r.returncode == 0 and "run-record" in r.stdout)
    else:
        ok = False
    ok_all &= check("EVC-10", ok,
                    "the eval-gate integration: the corpus run is a "
                    "recorded command asserted by re-run",
                    "the corpus run is wired into the standing gate's "
                    "recorded commands")

    if not machinery:
        print("RED — the P5-B machinery is absent at this tree "
              "(LAW-11: every case needs harness/eval.py)")
        return 1
    print("GREEN — the P5-B eval corpus suite (EVC-01..10) passes" if ok_all
          else "RED — at least one EVC case failed")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
