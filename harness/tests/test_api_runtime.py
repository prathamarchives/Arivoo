#!/usr/bin/env python3
"""harness/tests/test_api_runtime.py — Workstream 2 (production DB/runtime
integration): the API boundary's three honest-declaration contracts.

This suite is stdlib-only so it runs on BOTH the venv-less trusted runner and
the local rig (unlike the fastapi-dependent route battery). It checks:

  * ARV-RT-001  the CORS origin matrix is parsed by a strict, stdlib-only
                module: exact origins only, no wildcard, no paths/userinfo,
                bounded count, and an explicit refusal code on malformed input
  * ARV-RT-002  /health/ready's success predicate includes the DB declaration
                (a service with no open DB path must not report ready)
  * ARV-RT-003  the app installs real CORS middleware from the parsed matrix
  * ARV-RT-004  the ASGI entry derives readiness from the service environment
                and refuses a startup that would claim DB readiness it lacks

Zero third-party imports (LAW-08); fastapi's own behavior stays in the pinned
venv's route battery (harness/api/routes_selfcheck.py).
"""
import ast
import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
FAILS: list[str] = []


def check(code, ok, what, repair):
    print(("PASS " if ok else "FAIL ") + code + ": " + what)
    if not ok:
        print("      repair: " + repair)
        FAILS.append(code)


def _source(rel: str) -> str:
    p = REPO / rel
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def _cors_module():
    p = REPO / "harness" / "api" / "cors.py"
    if not p.is_file():
        return None
    spec = importlib.util.spec_from_file_location("arivo_api_cors_under_test", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ready_ok_includes_db(src: str) -> bool:
    """AST: the `ok` assignment inside the /health/ready handler must READ
    health_db_ready — a textual 'database' field alone is not a predicate."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name != "ready":
            continue
        for stmt in ast.walk(node):
            if not isinstance(stmt, ast.Assign):
                continue
            targets = [t.id for t in stmt.targets if isinstance(t, ast.Name)]
            if "ok" not in targets:
                continue
            return any(isinstance(n, ast.Name) and n.id == "health_db_ready"
                       for n in ast.walk(stmt.value))
    return False


def _installs_cors_from_env(src: str) -> bool:
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False
    add_middleware = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.attr if isinstance(fn, ast.Attribute) else (
            fn.id if isinstance(fn, ast.Name) else "")
        if name == "add_middleware" and any(
                isinstance(a, ast.Name) and a.id == "CORSMiddleware"
                for a in node.args):
            add_middleware = True
    return add_middleware and ("ARIVO_ALLOWED_ORIGINS" in src or "_cors.ENV_NAME" in src)


def main() -> int:
    mod = _cors_module()
    check("ARV-RT-001", mod is not None,
          "a stdlib-only CORS origin parser exists at harness/api/cors.py",
          "add harness/api/cors.py with a strict parse_allowed_origins()")
    if mod is not None:
        good = ("https://arivo.itscatalyst.com, http://localhost:5173")
        try:
            parsed = mod.parse_allowed_origins(good)
            check("ARV-RT-002", tuple(parsed) == (
                "https://arivo.itscatalyst.com", "http://localhost:5173"),
                "the exact origin matrix parses (comma-separated, stripped)",
                "parse the matrix into an exact tuple of origins")
        except Exception as e:
            check("ARV-RT-002", False, "the exact origin matrix parses",
                  f"parse_allowed_origins raised {type(e).__name__}")
        check("ARV-RT-003", tuple(mod.parse_allowed_origins("")) == (),
              "an empty matrix means CORS off, never a wildcard",
              "return an empty tuple for an unset matrix; never '*'")
        for i, bad in enumerate(("*", "https://arivo.itscatalyst.com/",
                                 "https://user@arivo.itscatalyst.com",
                                 "https://a, ,https://b"), start=1):
            refused = False
            try:
                mod.parse_allowed_origins(bad)
            except Exception as e:
                refused = ("ARV-CORS-001" in str(e))
            check(f"ARV-RT-004-{i}", refused,
                  f"malformed origin matrix refused ({bad})",
                  "refuse wildcards, paths, userinfo and empty entries with ARV-CORS-001")
        allowed = tuple(mod.parse_allowed_origins(good))
        check("ARV-RT-005", mod.is_allowed("https://arivo.itscatalyst.com", allowed)
              and not mod.is_allowed("https://evil.example", allowed),
              "origin matching is exact (no suffix or wildcard matching)",
              "is_allowed must compare the whole origin string")
    else:
        for code in ("ARV-RT-002", "ARV-RT-003", "ARV-RT-004", "ARV-RT-005"):
            check(code, False, "CORS behavior (parser absent)",
                  "add harness/api/cors.py first")

    app_src = _source("harness/api/app.py")
    check("ARV-RT-006", _ready_ok_includes_db(app_src),
          "/health/ready's ok predicate includes health_db_ready",
          "include the DB declaration in the readiness predicate")
    check("ARV-RT-007", _installs_cors_from_env(app_src),
          "the app installs CORSMiddleware from ARIVO_ALLOWED_ORIGINS",
          "wire the parsed matrix into starlette's CORSMiddleware in harness/api/app.py")

    main_src = _source("harness/api/__main__.py")
    check("ARV-RT-008", "ARIVO_DB_READY" in main_src and "ARV-SVC-002" in main_src
          and "health_db_ready=True" not in main_src,
          "the ASGI entry derives DB readiness from env and refuses an undeclared DB",
          "replace the hardcoded True with the env declaration + a named startup refusal")

    check("ARV-RT-009", "ARV-SVC-003" in main_src
          and "verify-full" in main_src and "arv_app" in main_src,
          "the ASGI entry declares the production DB path (verify-full, pinned CA, arv_app)",
          "add the named startup refusal for an undeclared production DB shape")

    print()
    if FAILS:
        print(f"RED — the API runtime boundary is not honest: {len(FAILS)} check(s) "
              f"failed ({', '.join(FAILS)}).")
        return 1
    print("GREEN — the API runtime boundary is honest: strict CORS origins, a "
          "DB-aware readiness predicate, and fail-closed startup declaration.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
