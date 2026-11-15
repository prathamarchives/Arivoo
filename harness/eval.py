#!/usr/bin/env python3
"""harness/eval.py — P5-B the eval corpus machinery (CLAIM-081, record 73 §2;
the PLAN 5B row: the versioned query corpus BEFORE any ranking change).

THE CONTRACT: the corpus is a versioned JSON file (the four case classes —
relevant / no-result / distractor / conflated); the run is DETERMINISTIC (the
same corpus id + revision re-runs byte-equal: no clock, no randomness, no
environment-dependent ordering — the verdict sorts and the ids are fixed);
the verdict is MECHANICAL (the expected vs the actual id sets; precision and
recall computed over the counts, printed with the corpus id + revision + the
per-class breakdown — never an LLM narration); the corpus is DATA (a hostile
query is evaluated like any other — nothing executes it); the run rides the
owner boundary (RLS through the standing _read path); an UNREGISTERED corpus
id refuses typed (ARV-EVL-001 — never a silent default); a malformed corpus
file refuses typed (ARV-EVL-002); a case with a malformed class refuses typed
(ARV-EVL-003). The run-record form: a JSON line in the slice's runs (the
EVC-10 pin's object).

The query machinery: harness/query.py's search arm (the standing keyword
core — the AND semantics, the tombstone parity, the authoritative current
revision, RLS). The evaluator NEVER re-implements retrieval; it calls the
arm and compares id sets.
"""
import json
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
RUNS = REPO / "harness" / "runs"
REGISTRY = {
    # the registered corpora (the EVC-09 law: an unregistered id refuses
    # typed, never a silent default)
    "arv-p5b-eval-corpus": {
        "file": "harness/runs/claim-081-p5b-eval-corpus/corpus.json",
        "revision": 1,
    },
}
ARV_EVL = {
    "001": "no such corpus registered (the registered corpora are the "
           "eval corpus registry's own files — never a silent default to "
           "another corpus)",
    "002": "the corpus file is malformed JSON or missing the required "
           "fields (corpus_id, revision, cases)",
    "003": "the case class is not one of the four (relevant, no-result, "
           "distractor, conflated) — the corpus is data under a contract",
    "004": "the search arm refused — an infrastructure failure is never "
           "the honest empty set (the round-1 D-042 repair: the arm's "
           "typed refusal propagates, the evaluator never converts a "
           "broken environment into a passing verdict)",
}


class ArmRefused(Exception):
    """The search arm's typed refusal (ARV-EVL-004's object)."""


def _fail(code: str, detail: str) -> int:
    print(f"FAIL ARV-EVL-{code}: {ARV_EVL[code]} — {detail}")
    return 1


def _search(db: str, owner: str, terms: list) -> list:
    """One query through the standing search arm; returns the id set.
    The round-1 D-042 repair: the arm's refusal propagates typed — a dead
    DB, a refused RLS read, or an arm-side typed failure is NEVER
    converted into the honest empty set (the fail-open closed)."""
    r = subprocess.run(
        [sys.executable, str(REPO / "harness" / "query.py"), "search",
         "--owner", owner, *terms],
        capture_output=True, text=True, timeout=240,
        env=dict(os.environ, PGDATABASE=db),
    )
    if r.returncode != 0 or "FAIL ARV-" in (r.stdout or ""):
        detail = (r.stdout or r.stderr or "").strip().split("\n")[0][:120]
        raise ArmRefused(f"the arm refused for terms {terms!r}: {detail}")
    ids = set()
    for ln in (r.stdout or "").split("\n"):
        if not ln or ln.startswith("#"):
            continue
        parts = ln.split("|")
        if len(parts) >= 2:
            ids.add(f"{parts[0]}|{parts[1]}")
    return sorted(ids)


def _owner_search(db: str, owner: str, terms: list) -> list:
    return _search(db, owner, terms)


def cmd_corpus_load(a) -> int:
    """the corpus load: the form check + the four-class summary (EVC-01)."""
    p = REPO / a.file
    if not p.is_file():
        return _fail("002", f"{a.file} is absent")
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return _fail("002", f"malformed JSON: {e}")
    for k in ("corpus_id", "revision", "cases"):
        if k not in d:
            return _fail("002", f"missing field {k}")
    classes = {}
    for c in d["cases"]:
        cls = c.get("class")
        if cls not in ("relevant", "no-result", "distractor", "conflated"):
            return _fail("003", f"case {c.get('case')}: class {cls!r}")
        classes[cls] = classes.get(cls, 0) + 1
    print(f"# corpus_id={d['corpus_id']} revision={d['revision']} "
          f"cases={len(d['cases'])}")
    print(f"# relevant={classes.get('relevant', 0)} "
          f"no-result={classes.get('no-result', 0)} "
          f"distractor={classes.get('distractor', 0)} "
          f"conflated={classes.get('conflated', 0)}")
    for c in sorted(d["cases"], key=lambda x: x["case"]):
        exp = c.get("expect_ids", [])
        print(f"case={c['case']} class={c['class']} "
              f"query={' '.join(c['query'])} expected={len(exp)}")
    return 0


def cmd_run(a) -> int:
    """the corpus run: the deterministic mechanical verdict (EVC-02..08)."""
    reg = REGISTRY.get(a.corpus)
    if reg is None:
        return _fail("001", f"corpus {a.corpus!r} is not registered")
    p = REPO / reg["file"]
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return _fail("002", f"{reg['file']}: {e}")
    if d.get("corpus_id") != a.corpus or d.get("revision") != a.revision:
        return _fail("002",
                     f"the file's id/revision ({d.get('corpus_id')}/"
                     f"{d.get('revision')}) != the requested "
                     f"({a.corpus}/{a.revision})")
    db = os.environ.get("PGDATABASE", "postgres")
    owner = a.owner or "A"
    tp = fp = fn = 0
    lines = []
    hostile_seen = 0
    try:
        for c in sorted(d["cases"], key=lambda x: x["case"]):
            cls = c["class"]
            actual = _owner_search(db, owner, c["query"])
            # the hostile-content marker (EVC-07): the query's words are DATA;
            # the run evaluates them exactly like any other case — no special
            # branch exists, so the only observable is the honest comparison
            if any(w in ("ignore", "corpus") for w in c["query"]) and cls == "conflated":
                hostile_seen += 1
            if cls == "relevant":
                # the round-1 D-042 repair (finding 3): the verdict is
                # COUNT-BASED against the corpus's expected count — the
                # over-admission channel: every admission beyond the
                # expected count is fp (precision can actually drop; a
                # ranking change that admits junk is visible), the
                # shortfall is fn. expect_count is the authoritative
                # expectation (the symbolic expect_ids are the corpus's
                # descriptive form; the count is the verdict's own)
                exp_n = int(c.get("expect_count",
                                  len(c.get("expect_ids", [])) or 0))
                tp += min(len(actual), exp_n)
                if len(actual) > exp_n:
                    fp += len(actual) - exp_n
                elif len(actual) < exp_n:
                    fn += exp_n - len(actual)
                lines.append(f"case={c['case']} class=relevant "
                             f"actual={len(actual)} expected={exp_n}")
            elif cls == "no-result":
                empty = len(actual) == 0
                if not empty:
                    fp += len(actual)
                lines.append(f"case={c['case']} class=no-result "
                             f"actual={len(actual)} expected=0 "
                             f"empty={'true' if empty else 'false'} "
                             f"{'the honest empty set' if empty else 'FABRICATED'}")
            elif cls == "distractor":
                # the round-1 D-042 repair (finding 2): the real distractor
                # control — the expected count is 0 (the near-miss material
                # must NOT be admitted); every admission is fp and the
                # shortfall (an empty verdict where the corpus EXPECTS the
                # near-miss to exist-but-not-admit... no: the distractor's
                # expectation IS zero admissions) — the dead tautology
                # (clean = miss == len(actual)) is deleted; the admission
                # count over the recorded expectation is the whole verdict
                exp_n = int(c.get("expect_count", 0))
                if len(actual) > exp_n:
                    fp += len(actual) - exp_n
                elif len(actual) < exp_n:
                    fn += exp_n - len(actual)
                lines.append(f"case={c['case']} class=distractor "
                             f"admitted={len(actual)} expected={exp_n} "
                             f"near-miss-excluded="
                             f"{'true' if len(actual) == exp_n else 'false'}")
            else:  # conflated
                # the round-1 D-042 repair (finding 3, the conflated half):
                # the same count-based channel — the expected count is the
                # recorded expect_count (the BOTH documents); the
                # rank-suppression of the second document is fn, the
                # over-admission beyond the pair is fp
                exp_n = int(c.get("expect_count", 2))
                tp += min(len(actual), exp_n)
                if len(actual) > exp_n:
                    fp += len(actual) - exp_n
                elif len(actual) < exp_n:
                    fn += exp_n - len(actual)
                lines.append(f"case={c['case']} class=conflated "
                             f"admitted={len(actual)} expected={exp_n} "
                             f"both={'true' if len(actual) >= exp_n else 'false'}")
    except ArmRefused as e:
        return _fail("004", str(e))
    prec = (tp / (tp + fp)) if (tp + fp) else 1.0
    rec = (tp / (tp + fn)) if (tp + fn) else 1.0
    print(f"# corpus_id={a.corpus} revision={a.revision} owner={owner} "
          f"cases={len(d['cases'])} hostile-as-data={hostile_seen}")
    for ln in lines:
        print(ln)
    print(f"# verdict precision={prec:.4f} recall={rec:.4f} "
          f"tp={tp} fp={fp} fn={fn} classes=4")
    # EVC-10: the run-record form — the JSON line appended to the slice runs
    rec_p = RUNS / "claim-081-p5b-eval-corpus" / "eval-runs.jsonl"
    rec_p.parent.mkdir(parents=True, exist_ok=True)
    entry = {"corpus_id": a.corpus, "revision": a.revision, "owner": owner,
             "precision": round(prec, 4), "recall": round(rec, 4),
             "tp": tp, "fp": fp, "fn": fn, "cases": len(d["cases"])}
    with rec_p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("# run-record appended (the EVC-10 pin's object: the JSONL line "
          "in the slice runs)")
    return 0


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="eval.py",
                                  description="the P5-B eval corpus machinery")
    sub = ap.add_subparsers(dest="what", required=True)
    p = sub.add_parser("corpus")
    p.add_argument("cmd", choices=["load"])
    p.add_argument("--file", required=True)
    p = sub.add_parser("run")
    p.add_argument("--corpus", required=True)
    p.add_argument("--revision", type=int, default=1)
    p.add_argument("--owner", default=None)
    a = ap.parse_args()
    if a.what == "corpus":
        return cmd_corpus_load(a)
    return cmd_run(a)


if __name__ == "__main__":
    sys.exit(main())
