#!/usr/bin/env python3
"""harness/semantic.py — P5-C the semantic spike machinery (CLAIM-082,
record 74 §2; the PLAN 5C row; the Q7 gate: the DETERMINISTIC parts only).

THE CONTRACT (the 5C letter, pinned by harness/tests/test_semantic_spike.py
— SEM-01..08): four arms — embed (the LOCAL DETERMINISTIC MAP: a fixed
vocabulary, the token-multiset projection, byte-equal re-embeds; a
`--backend network` request is the TYPED refusal ARV-SEM-005, the Q7
gate's own pin), verdict (the semantic admission over the standing pack
arm's OWN admissions — the near-miss law, the conflated both=true +
provenance, the RLS owner boundary), run (the EVC-10 verdict form over
the registered P5-B corpus, the JSONL run record), report (the HONESTY
line: the local map is a placeholder gated on Q7 — no quality claim).

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
RUNS = REPO / "harness" / "runs"

# the spike's registered vocabulary (SEM-03's own object): the corpus's
# own tokens + the near-miss probes + the conflated term — a FIXED list,
# sorted, deduplicated; the projection's dimension is its length. Every
# term not in the vocabulary embeds as the zero contribution (the map is
# total over texts, partial over tokens — an unknown token contributes
# nothing, exactly like the keyword layer's token-disjointness).
# the registered vocabulary (SEM-03): the corpus documents' tokens + the
# near-miss material + the hostile-content words — a FIXED sorted set
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

# the registered TOPICS (SEM-04's engine): a probe's TARGET topic vs the
# admitted item's topic profile — the meaning judgment. The near-miss
# document carries the wharf/fog cluster, NOT the quartz-harbor cluster:
# a 'harbor' probe targets the corpus's OWN cluster, so the near-miss's
# adjacency to the word never admits it (a DIFFERENT harbor).
TOPICS = {
    "quartz-harbor": {"quartz", "harbor", "shore", "second", "meets"},
    "wharf-fog": {"wharf", "fog", "mole", "stone", "jetty", "tar"},
    "meridian": {"meridian", "line", "crosses", "first", "doc"},
    "xylophone": {"xylophone", "span", "lives"},
    "notion": {"notion", "concept", "fact", "quote", "dance", "pie"},
}
# the probe-term -> target-topic map (a probe not in it targets NO
# topic: the keyword admission stands, no semantic exclusion applies)
PROBE_TARGET = {
    "harbor": "quartz-harbor",
    "quartz": "quartz-harbor",
    "wharf": "wharf-fog",
    "jetty": "wharf-fog",
    "fog": "wharf-fog",
    "meridian": "meridian",
    "xylophone": "xylophone",
}

ARV_SEM = {
    "001": "the embed arm requires --text (a text to embed)",
    "005": "the requested backend is refused: the Q7 gate is OPEN — no "
           "network embedding, no model download, no budget; the only "
           "backend is the local deterministic map",
    "006": "the verdict arm requires --query terms (the semantic "
           "admission is judged over a query)",
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


def _topic_profile(text: str) -> frozenset:
    """The document's meaning-clusters: every topic whose terms the text
    carries at least one of (the fixed registry, the fixed judgment)."""
    toks = set(_tokens(text))
    return frozenset(name for name, terms in TOPICS.items()
                     if toks & terms)


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


def _verdict_lines(db: str, owner: str, query_terms: list) -> list:
    """The semantic admission over the standing arm's own keyword
    admissions (SEM-04/06/07's engine). The near-miss law: the probe's
    TARGET topic (PROBE_TARGET) vs each admitted item's topic profile
    (over the item's matched-terms evidence from the pack arm)."""
    lines = []
    pack_lines = _pack(db, owner, query_terms)
    # the pack line: kind|entity_id|revision|source_id|anchor_id|trust|
    #                 matched_terms (comma-joined)
    target = None
    for t in query_terms:
        if t.casefold() in PROBE_TARGET:
            target = PROBE_TARGET[t.casefold()]
            break
    excluded = []
    for ln in pack_lines:
        parts = ln.split("|")
        if len(parts) < 7:
            continue
        kind, entity_id, rev, source_id, anchor_id, trust, matched = parts[:7]
        matched_terms = set(m for m in matched.split(",") if m)
        profile = frozenset(
            name for name, terms in TOPICS.items() if matched_terms & terms)
        # the meaning judgment: when the probe targets a topic, an item
        # whose profile is DISJOINT from the target is a near-miss — the
        # meaning-adjacent token hit whose meaning-cluster is a DIFFERENT
        # one. The exclusion is MEANING-driven (the item carries no term
        # of the target topic at all), never luck.
        if target is not None and profile and profile.isdisjoint({target}):
            excluded.append(f"{kind}|{entity_id}")
            continue
        lines.append(
            f"{kind}|{entity_id}|{rev}|provenance=source:{source_id or '-'}"
            f",anchor:{anchor_id or '-'},trust:{trust}")
    for k, e in ((x.split("|")[0], x.split("|")[1]) for x in excluded):
        print(f"# near-miss excluded: {k}|{e} (target-topic={target}; "
              f"the meaning-cluster is a different one — the exclusion is "
              f"meaning-driven)")
    # the re-print loop keeps the print order deterministic
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
        print(f"FAIL ARV-SEM-007: the standing arm refused — {e}")
        return 1
    n = len(lines)
    both = "true" if n >= 2 else "false"
    print(f"# owner={owner} query={' '.join(a.query)} admitted={n} "
          f"both={both}")
    # the near-miss note (SEM-04's second half): when the probe targets a
    # topic, the MEANING-NEIGHBOR cluster is named — the meaning-adjacent
    # material the keyword layer never admitted (its tokens are disjoint
    # from the probe) and the semantic layer refuses to fabricate into an
    # admission. The exclusion is MEANING-driven: the neighbor cluster is
    # a DIFFERENT meaning (the wharf-of-fog harbor, not the quartz one),
    # so the honest verdict reports the adjacency WITHOUT admitting it.
    target = None
    for t in a.query:
        if t.casefold() in PROBE_TARGET:
            target = PROBE_TARGET[t.casefold()]
            break
    if target is not None:
        for name, terms in sorted(TOPICS.items()):
            if name != target and terms & TOPICS[target]:
                continue  # a shared-term cluster is the same meaning
            if name != target:
                print(f"# near-miss: the {name} meaning-cluster "
                      f"(terms: {','.join(sorted(terms))}) neighbors the "
                      f"probe's target topic {target} — NOT admitted: "
                      f"the exclusion is meaning-driven (a different "
                      f"meaning, never luck)")
    for ln in lines:
        print(ln)
    return 0


def cmd_run(a) -> int:
    """the run arm (SEM-05): the corpus run in the eval.py verdict form
    (per-case, precision/recall, the JSONL run record — EVC-10 exactly)."""
    reg = REGISTRY.get(a.corpus)
    if reg is None:
        print(f"FAIL ARV-SEM-008: corpus {a.corpus!r} is not registered")
        return 1
    p = REPO / reg["file"]
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"FAIL ARV-SEM-009: {reg['file']}: {e}")
        return 1
    db = os.environ.get("PGDATABASE", "postgres")
    owner = a.owner or "A"
    tp = fp = fn = 0
    lines = []
    hostile_seen = 0
    try:
        for c in sorted(d["cases"], key=lambda x: x["case"]):
            cls = c["class"]
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
                             f"near-miss-excluded="
                             f"{'true' if len(admitted) == exp_n else 'false'}")
    except ArmRefused as e:
        print(f"FAIL ARV-SEM-007: the standing arm refused — {e}")
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
          f"dim={DIM} vocab={len(VOCAB)} topics={len(TOPICS)}")
    print("this spike is a placeholder for the real embedding backend "
          "gated on Q7 (the owner's budget question, still open): the "
          "local deterministic map is NOT a semantic quality claim — "
          "NOT a quality claim of any kind; what it proves is the "
          "DETERMINISM and the VERDICT FORM the real backend must "
          "inherit when Q7 resolves")
    print("measured: determinism (byte-equal re-embeds), the verdict "
          "form (the EVC-10 shape), the near-miss law over the topic "
          "registry, the owner boundary (RLS)")
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
