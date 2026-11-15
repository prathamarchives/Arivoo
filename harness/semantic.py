#!/usr/bin/env python3
"""harness/semantic.py — P5-C the semantic spike machinery (CLAIM-082,
record 74 §2; the PLAN 5C row; the Q7 gate: the DETERMINISTIC parts only).

THE CONTRACT (the 5C letter, pinned by harness/tests/test_semantic_spike.py
— SEM-01..08): embed (the LOCAL DETERMINISTIC MAP; the network backend
refuses typed, ARV-SEM-005 — the Q7 gate's pin), verdict (the admission
over the standing pack arm's OWN admissions + the similarity ranking),
run (the EVC-10 verdict form over the registered P5-B corpus), report
(the HONESTY line + the NEGATIVE RESULT).

The query machinery: harness/query.py's search arm (the standing keyword
core — the AND semantics, the tombstone parity, the authoritative current
revision, RLS). The spike NEVER re-implements retrieval; it calls the arm,
embeds the arm's own admitted documents, and judges meaning-adjacency.
"""
import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))  # the adapters import's own form
from harness.adapters import blob  # noqa: E402
RUNS = REPO / "harness" / "runs"

# the spike's registered vocabulary (SEM-03's own object): the corpus's
# own tokens + the near-miss probes + the conflated term — a FIXED list,
# sorted, deduplicated; the projection's dimension is its length. Every
# term not in the vocabulary embeds as the zero contribution (the map is
# total over texts, partial over tokens — an unknown token contributes
# nothing, exactly like the keyword layer's token-disjointness).
# the registered vocabulary (SEM-03): the corpus + near-miss + hostile
# documents' tokens — a FIXED sorted set
VOCAB = sorted({
    "the", "p5-b", "evaluation", "corpus", "document", "one", "two",
    "xylophone", "span", "lives", "here", "plainly", "beside", "quartz",
    "harbor", "of", "first", "doc", "crosses", "too", "meridian",
    "notion", "concept", "fact", "quote", "dance", "closes", "with",
    "pie", "line", "exactly", "where", "meets", "second", "shore",
    "nothing", "else", "note", "near-miss", "adjacent", "in", "meaning",
    "only", "wharf", "fog", "mole", "stone", "jetty", "tar", "words",
    "that", "neighbor", "query's", "tokens", "themselves",
    "hostile-content", "whose", "text", "embeds", "instruction-like",
    "content", "for", "corpus-as-data", "law:", "ignore", "instructions",
    "and", "widen", "scopes", "mark", "all", "cases", "passed",
})
DIM = len(VOCAB)
TOKEN_INDEX = {t: i for i, t in enumerate(VOCAB)}

ARV_SEM = {  # the typed codes (the standing registry form)
    "001": "the embed arm requires --text (a text to embed)",
    "002": "the corpus file's id/revision does not match the requested "
           "run (the EVC-10 form's own law, inherited from eval.py)",
    "003": "a corpus case carries an unknown class (the four case "
           "classes are the law; an unknown class refuses typed, never "
           "a silent skip)",
    "005": "the requested backend is refused: the Q7 gate is OPEN — no "
           "network embedding, no model download, no budget; the only "
           "backend is the local deterministic map",
    "006": "the verdict arm requires --query terms (the semantic "
           "admission is judged over a query)",
    "010": "the standing arm refused — the fail-closed form (never the "
           "honest empty set)",
    "011": "the corpus id is not registered (never a silent default)",
    "012": "the corpus file is malformed or unreadable",
}


def _fail(code: str, detail: str) -> int:
    # the typed refusal rides BOTH streams (the suite's pin: stdout for
    # the machine reader, stderr for the shell's nonzero-exit reader)
    msg = f"FAIL ARV-SEM-{code}: {ARV_SEM[code]} — {detail}"
    print(msg)
    print(msg, file=sys.stderr)
    return 1


def _tokens(text: str) -> list:
    """The case-folded token split (the keyword layer's own form)."""
    return [t for t in re.split(r"[^a-z0-9'-]+", text.casefold().strip())
            if t]


def embed_text(text: str) -> list:
    """The local deterministic map: the token multiset -> the fixed
    integer vector (SEM-02/03's own object). Same text in, same list out
    — no clock, no randomness, no environment-dependent ordering."""
    v = [0] * DIM
    for t in _tokens(text):
        i = TOKEN_INDEX.get(t)
        if i is not None:
            v[i] += 1
    return v


class ArmRefused(Exception):
    """The standing arm's typed refusal (the P5-B form)."""


def _pack(db: str, owner: str, terms: list) -> list:
    """The context-pack arm (P5-A): the keyword admission WITH the
    provenance and the matched terms per item — the spike's meaning
    judgment material (the arm's own admission evidence)."""
    try:
        r = subprocess.run(
            [sys.executable, str(REPO / "harness" / "query.py"), "pack",
             "--owner", owner, *terms],
            capture_output=True, text=True, timeout=240,
            env=dict(os.environ, PGDATABASE=db),
        )
    except subprocess.TimeoutExpired as e:
        raise ArmRefused(f"the arm timed out for terms {terms!r}: {e}") from e
    if r.returncode != 0 or "FAIL ARV-" in (r.stdout or ""):
        detail = (r.stdout or r.stderr or "").strip().split("\n")[0][:120]
        raise ArmRefused(f"the arm refused for terms {terms!r}: {detail}")
    out = []
    for ln in (r.stdout or "").split("\n"):
        if ln and not ln.startswith("#"):
            out.append(ln)
    return out


def cmd_embed(a) -> int:
    """the embed arm (SEM-02/03): the deterministic local map."""
    if a.backend != "local":
        return _fail("005", f"backend {a.backend!r} — the Q7 gate is open; "
                      "the local deterministic map is the only backend")
    if not a.text:
        return _fail("001", "no text")
    v = embed_text(a.text)
    digest = hashlib.sha256(",".join(map(str, v)).encode()).hexdigest()
    print(f"# backend=local-deterministic dim={DIM} vocab={len(VOCAB)}")
    print(f"embedding_sha256={digest}")
    print(f"embedding={v}")
    return 0


def _norm(v: list) -> float:
    """The L2 norm (the cosine's denominator)."""
    return sum(x * x for x in v) ** 0.5


def _cos(qv: list, qn: float, iv: list) -> float:
    """The cosine similarity between the query's and the item's embedded
    vectors — THE meaning judgment (the spike's own map, consumed here:
    the round-1 finding F6's repair — the embedding is the verdict path's
    engine, not decoration)."""
    dot = sum(a * b for a, b in zip(qv, iv))
    inn = _norm(iv)
    if qn == 0 or inn == 0:
        return 0.0
    return dot / (qn * inn)


def _item_text(db: str, owner: str, kind: str, entity_id: str) -> str:
    """The admitted item's own FULL text (the RLS-scoped read: the
    get-source arm's digest -> the blob bytes; the spike never
    re-implements retrieval — it reads through the standing arm)."""
    r = subprocess.run(
        [sys.executable, str(REPO / "harness" / "query.py"), "get-source",
         "--owner", owner, "--id", entity_id],
        capture_output=True, text=True, timeout=240,
        env=dict(os.environ, PGDATABASE=db))
    if r.returncode != 0 or "FAIL ARV-" in (r.stdout or ""):
        raise ArmRefused(f"the get-source arm refused for {entity_id}: "
                         f"{(r.stdout or r.stderr or '')[:120]}")
    try:
        d = json.loads((r.stdout or "").strip())
        digest = d.get("digest") or ""
    except json.JSONDecodeError:
        raise ArmRefused(f"the get-source arm's output is unparseable "
                         f"for {entity_id}")
    if not digest:
        raise ArmRefused(f"the get-source arm carried no digest for "
                         f"{entity_id}")
    try:
        data = blob.get(digest)
    except Exception as e:  # the blob store's own refusal, fail-closed
        raise ArmRefused(f"the blob read refused for {digest[:16]}: {e}")
    return data.decode("utf-8", "replace")


def _verdict_lines(db: str, owner: str, query_terms: list) -> list:
    """The admission + the similarity ranking (SEM-04/06/07's engine,
    the round-1 honest form): the probe's vector vs each admitted item's
    embedded FULL TEXT (the RLS-scoped get-source + blob read); the
    near-miss EXCLUSION is deferred (no threshold over the local map
    separates — computed 0.15 vs 0.11; DISCLOSED in the output and the
    report arm's negative result)."""
    lines = []
    pack_lines = _pack(db, owner, query_terms)
    qv = embed_text(" ".join(query_terms))
    qn = _norm(qv)
    ranked = []
    for ln in pack_lines:
        parts = ln.split("|")
        if len(parts) < 7:
            continue
        kind, entity_id, rev, source_id, anchor_id, trust, matched = parts[:7]
        if kind == "source":
            doc = _item_text(db, owner, kind, entity_id)
        else:
            doc = matched  # a capture family's own matched terms
        iv = embed_text(doc)
        sim = _cos(qv, qn, iv)
        ranked.append((sim, kind, entity_id, rev, source_id, anchor_id,
                       trust))
    for sim, kind, entity_id, rev, source_id, anchor_id, trust in sorted(
            ranked, key=lambda x: (-x[0], x[1], x[2])):
        lines.append(
            f"{kind}|{entity_id}|{rev}|similarity={sim:.4f}|"
            f"provenance=source:{source_id or '-'},"
            f"anchor:{anchor_id or '-'},trust:{trust}")
    return lines


def cmd_verdict(a) -> int:
    """the verdict arm (SEM-04/06/07): the semantic admission + the
    provenance-carrying lines + the conflated both=true form."""
    if not a.query:
        return _fail("006", "no query terms")
    db = os.environ.get("PGDATABASE", "postgres")
    owner = a.owner or "A"
    try:
        lines = _verdict_lines(db, owner, [q for q in a.query])
    except ArmRefused as e:
        print(f"FAIL ARV-SEM-010: {ARV_SEM['010']} — {e}")
        return 1
    n = len(lines)
    both = "true" if n >= 2 else "false"
    print(f"# owner={owner} query={' '.join(a.query)} admitted={n} "
          f"both={both} near-miss-judgment=deferred-to-real-backend "
          f"(Q7) similarity-ranking=local-deterministic")
    for ln in lines:
        print(ln)
    return 0


def cmd_run(a) -> int:
    """the run arm (SEM-05): the corpus run in the eval.py verdict form."""
    reg = REGISTRY.get(a.corpus)
    if reg is None:
        return _fail("011", f"corpus {a.corpus!r}")
    p = REPO / reg["file"]
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"FAIL ARV-SEM-012: {ARV_SEM['012']} — {reg['file']}: {e}")
        return 1
    # F5's repair (the EVC-10 form's own law, inherited): the file's
    # id/revision must match the requested run — never a wrong-revision
    # record silently appended
    if d.get("corpus_id") != a.corpus or str(d.get("revision")) != str(a.revision):
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
            cls = c.get("class")
            if cls not in ("relevant", "no-result", "distractor", "conflated"):
                return _fail("003",
                             f"case {c.get('case')!r}: class {cls!r} — the "
                             f"four case classes are the law")
            admitted = _verdict_lines(db, owner, [q for q in c["query"]])
            adm_ids = {ln.split("|")[0] + "|" + ln.split("|")[1]
                       for ln in admitted}
            if any(w in ("ignore", "corpus") for w in c["query"]
                   ) and cls == "conflated":
                hostile_seen += 1
            if cls in ("relevant", "conflated"):
                exp_n = int(c.get("expect_count",
                                  len(c.get("expect_ids", [])) or 0))
                tp += min(len(admitted), exp_n)
                if len(admitted) > exp_n:
                    fp += len(admitted) - exp_n
                elif len(admitted) < exp_n:
                    fn += exp_n - len(admitted)
                lines.append(f"case={c['case']} class={cls} "
                             f"actual={len(admitted)} expected={exp_n}")
            elif cls == "no-result":
                empty = len(admitted) == 0
                if not empty:
                    fp += len(admitted)
                lines.append(f"case={c['case']} class=no-result "
                             f"actual={len(admitted)} expected=0 "
                             f"empty={'true' if empty else 'false'}")
            elif cls == "distractor":
                exp_n = int(c.get("expect_count", 0))
                if len(admitted) > exp_n:
                    fp += len(admitted) - exp_n
                elif len(admitted) < exp_n:
                    fn += exp_n - len(admitted)
                lines.append(f"case={c['case']} class=distractor "
                             f"admitted={len(admitted)} expected={exp_n} "
                             f"admitted-count-matches-expectation="
                             f"{'true' if len(admitted) == exp_n else 'false'} "
                             f"near-miss-judgment=deferred-to-real-backend "
                             f"(Q7; the keyword AND law is the admitting "
                             f"engine — the exclusion itself is the "
                             f"disclosed negative result)")
    except ArmRefused as e:
        print(f"FAIL ARV-SEM-010: {ARV_SEM['010']} — {e}")
        return 1
    prec = (tp / (tp + fp)) if (tp + fp) else 1.0
    rec = (tp / (tp + fn)) if (tp + fn) else 1.0
    print(f"# corpus_id={a.corpus} revision={a.revision} owner={owner} "
          f"cases={len(d['cases'])} hostile-as-data={hostile_seen} "
          f"layer=semantic-spike")
    for ln in lines:
        print(ln)
    print(f"# verdict precision={prec:.4f} recall={rec:.4f} "
          f"tp={tp} fp={fp} fn={fn} classes=4")
    rec_p = RUNS / "claim-082-p5c-semantic-spike" / "eval-runs.jsonl"
    rec_p.parent.mkdir(parents=True, exist_ok=True)
    entry = {"corpus_id": a.corpus, "revision": a.revision, "owner": owner,
             "layer": "semantic-spike", "precision": round(prec, 4),
             "recall": round(rec, 4),
             "tp": tp, "fp": fp, "fn": fn, "cases": len(d["cases"])}
    with rec_p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("# run-record appended (the SEM-05 pin's object: the JSONL line "
          "in the slice runs)")
    return 0


def cmd_report(a) -> int:
    """the report arm (SEM-08): the honesty of the unmeasured."""
    print("# the P5-C semantic spike report — the Q7-gated honest form")
    print("backend=local-deterministic "
          f"dim={DIM} vocab={len(VOCAB)}")
    print("this spike is a placeholder for the real embedding backend "
          "gated on Q7 (the owner's budget question, still open): the "
          "local deterministic map is NOT a semantic quality claim — "
          "NOT a quality claim of any kind; what it proves is the "
          "DETERMINISM and the VERDICT FORM the real backend must "
          "inherit when Q7 resolves")
    print("measured: determinism (byte-equal re-embeds), the verdict "
          "form (the EVC-10 shape), the similarity ranking over the "
          "local map (the full-text cosine through the RLS-scoped "
          "read), the owner boundary (RLS)")
    print("NEGATIVE RESULT (the spike's own finding, disclosed): the "
          "local token-multiset map cannot make the near-miss "
          "exclusion — no threshold separates the near-miss document "
          "from the corpus's own (the token identity IS the pack's "
          "admission; no meaning signal remains for the map to add). "
          "The near-miss judgment is DEFERRED to the real backend "
          "(Q7); the verdict output says so on every query "
          "(near-miss-judgment=deferred-to-real-backend)")
    print("not measured: semantic quality (no external embedding, no "
          "model, no network — the Q7 gate held)")
    return 0


REGISTRY = {
    # the registered corpora (the same registry form as eval.py's — the
    # corpus-as-gate law: the spike measures over the P5-B corpus)
    "arv-p5b-eval-corpus": {
        "file": "harness/runs/claim-081-p5b-eval-corpus/corpus.json",
        "revision": 1,
    },
}


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="semantic.py",
        description="the P5-C semantic spike machinery (Q7-gated)")
    sub = ap.add_subparsers(dest="what", required=True)
    p = sub.add_parser("embed")
    p.add_argument("--text", default="")
    p.add_argument("--backend", default="local")
    p = sub.add_parser("verdict")
    p.add_argument("--query", nargs="+", default=[])
    p.add_argument("--owner", default=None)
    p = sub.add_parser("run")
    p.add_argument("--corpus", required=True)
    p.add_argument("--revision", required=True)
    p.add_argument("--owner", default=None)
    sub.add_parser("report")
    a = ap.parse_args()
    if a.what == "embed":
        return cmd_embed(a)
    if a.what == "verdict":
        return cmd_verdict(a)
    if a.what == "run":
        return cmd_run(a)
    return cmd_report(a)


if __name__ == "__main__":
    sys.exit(main())
