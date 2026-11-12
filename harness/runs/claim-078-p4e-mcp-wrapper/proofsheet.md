# PROOF SHEET — slice claim-078-p4e-mcp-wrapper (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 9f526e68832988d0ff8bf0bbf0d15ba5cdea9b09
- generated (last record's timestamp): 2026-11-12T07:57:10.533662+00:00
- run records: 23

## Run records (command, exit, output digest)
- `python3 harness/tests/test_mcp_wrapper.py` -> exit 0 · output sha256 dccd664b0b68ae24 · 2026-11-12T05:28:00.124632+00:00
- `python3 harness/tests/test_mcp_wrapper.py` -> exit 0 · output sha256 dccd664b0b68ae24 · 2026-11-12T05:28:07.540646+00:00
- `python3 harness/tests/test_mcp_wrapper.py` -> exit 0 · output sha256 dccd664b0b68ae24 · 2026-11-12T05:28:12.230021+00:00
- `make verify` -> exit 0 · output sha256 81a6b0ac452e2113 · 2026-11-12T05:35:41.829875+00:00
- `python3 harness/tests/test_mcp_wrapper.py` -> exit 1 · output sha256 de7ba27fafb77769 · 2026-11-12T06:16:04.594405+00:00
- `python3 harness/tests/test_mcp_wrapper.py` -> exit 0 · output sha256 192b0dd04eb00ccc · 2026-11-12T06:17:03.232809+00:00
- `python3 harness/tests/test_mcp_wrapper.py` -> exit 0 · output sha256 192b0dd04eb00ccc · 2026-11-12T06:17:08.103171+00:00
- `python3 harness/tests/test_mcp_wrapper.py` -> exit 0 · output sha256 192b0dd04eb00ccc · 2026-11-12T06:17:12.939439+00:00
- `make verify` -> exit 0 · output sha256 60f433de2d0ee0a3 · 2026-11-12T06:24:33.861140+00:00
- `python3 harness/tests/test_mcp_wrapper.py` -> exit 1 · output sha256 faea83728184f0fe · 2026-11-12T06:57:47.989437+00:00
- `python3 harness/tests/test_mcp_wrapper.py` -> exit 0 · output sha256 d242dfa3a69ecf20 · 2026-11-12T06:58:28.549260+00:00
- `python3 harness/tests/test_mcp_wrapper.py` -> exit 0 · output sha256 d242dfa3a69ecf20 · 2026-11-12T06:58:33.374127+00:00
- `python3 harness/tests/test_mcp_wrapper.py` -> exit 0 · output sha256 d242dfa3a69ecf20 · 2026-11-12T06:58:38.200698+00:00
- `make verify` -> exit 0 · output sha256 b7ce42de8e639279 · 2026-11-12T07:06:02.579194+00:00
- `env SLICE=claim-078-p4e-mcp-wrapper GATE_DIFF=origin/main make gate` -> exit 2 · output sha256 e8120ef5a6a4bdc5 · 2026-11-12T07:17:24.238089+00:00
- `env SLICE=claim-078-p4e-mcp-wrapper GATE_DIFF=origin/main make gate` -> exit 0 · output sha256 c9af13f17e8506f4 · 2026-11-12T07:40:38.046342+00:00
- `env ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-078-p4e-mcp-wrapper python3 -I /home/z/my-project/verification/anchored/trusted_gate_anchored.py --repo /home/z/my-project/Arivoo --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 0 · output sha256 954328615ea807b8 · 2026-11-12T07:41:17.568826+00:00
- `python3 harness/tests/test_mcp_wrapper.py` -> exit 0 · output sha256 d242dfa3a69ecf20 · 2026-11-12T07:42:24.623637+00:00
- `python3 harness/tests/test_mcp_wrapper.py` -> exit 0 · output sha256 d242dfa3a69ecf20 · 2026-11-12T07:42:29.507259+00:00
- `python3 harness/tests/test_mcp_wrapper.py` -> exit 0 · output sha256 d242dfa3a69ecf20 · 2026-11-12T07:42:34.403932+00:00
- `make verify` -> exit 0 · output sha256 8817b5eff893fdfd · 2026-11-12T07:49:45.462650+00:00
- `env SLICE=claim-078-p4e-mcp-wrapper GATE_DIFF=origin/main make gate` -> exit 0 · output sha256 aeb6b3d9cc58f8ed · 2026-11-12T07:56:45.580509+00:00
- `env ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-078-p4e-mcp-wrapper python3 -I /home/z/my-project/verification/anchored/trusted_gate_anchored.py --repo /home/z/my-project/Arivoo --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 0 · output sha256 7045e462e4522695 · 2026-11-12T07:57:10.533662+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - CLAIM-078 — the honest not-verified list (LAW-04: the explicit statement, never
- empty-by-omission). The full SEV account: sev.json + sev-round-1.md + sev-round-2.md.
- - - F-078-2 (P3, ROUTED): a tools/call sent BEFORE any initialize is served — the MCP
- spec's ordering is a client-side SHOULD NOT and the slice letter claims no pre-init
- rejection; rejecting would need the spec's -32002 class (a future hardening increment,
- never claimed here). Observed live by both rounds; every pre-init read still
- credential-scoped and audited.
- - - F-078-3 (P3, ROUTED): a request with "id": null is answered with "id": null — the
- faithful JSON-RPC echo (discouraged from clients, harmless to answer).
- - - F-078-4 (P3, ROUTED): invalid UTF-8 on stdin survives under the rig's default locale
- (utf-8/surrogateescape) — answered -32700, the session continuing; a strict
- PYTHONIOENCODING=utf-8:strict override kills the process at the decode. An environment
- property, not a wrapper behavior; the delivered rig and the CI default are the surviving
- configuration.
- - - F2-078-2 (P3, ROUTED — PRODUCT-side, outside this slice's diff): the retrieval core
- itself (pg.py's _run_psql) dies with an UNTYPED OSError "[Errno 7] Argument list too
- long: 'psql'" traceback when a read argument pushes the SQL past the psql -c argv limit
- (~131k chars, the kernel's MAX_ARG_STRLEN) — the substrate's named-code law violated at
- the oversize boundary; the wrapper's own claims hold there (isError, byte-preserving,
- no crash, no audit row). Joins the F-075-1/F-076-1 untyped-traceback family at the
- substrate grammar owner's slice.
- - - the resource-exhaustion classes unprobed and unclaimed: a ~100MB single line (the
- same exposure any line-based JSON-RPC peer has); a ~100k-term search riding the
- unchanged 240s READ_TIMEOUT arm (answered -32603 without ARV-MCP-003 — the timeout
- arm, unchanged by the repairs); memory exhaustion. No DoS claims are made (the local
- single-user threat model).
- - - the json recursion cliff is interpreter-dependent: bracketed live at (9000 parses,
- 10000 raises) on this rig's CPython 3.12.16; the MCPW-10 pin demonstrates at depth
- 20000. A wrapper-level depth budget (interpreter-independent) would be a future
- increment.
- - - no concurrency or load claims (single-client rigs; the round-2 reviewer ran two
- concurrent instances scope-correct, never a load claim).
- - - the byte-equality law verified as decoded-UTF-8 string equality (both sides decode
- the same bytes; the transport's ensure_ascii=False re-encoding exercised, not
- byte-inspected).
- - - the no-token-in-argv proof is behavioral + static (the two-channel refusal + the
- env-only serving + the AST argv inspection jointly establish it; not a ptrace of the
- child's execve).
- - - Q10's honest boundary: the environment channel is visible to the same user's
- processes (narrows argv exposure; NOT a multi-user isolation mechanism); stdio only
- (no HTTP/SSE transport, never claimed); the hash comparison non-constant-time (slice
- one's standing residual); no token rotation/expiry windows; the minting policy and any
- server-deployment scoping stay owner-gated.
- - - the bounded exclusions of §2 carry: no write scopes; no MCP resources/prompts
- surfaces (tools only); no HTTP/SSE; no new migration (the 0019 substrate serves
- unchanged); no reader-client work (P4-B's repo); no Phase 5 retrieval machinery (the
- deeper response budgets).
- - - the standing family-wide classes carry forward unchanged: the F-072-1 _nte_canon_id
- pattern, the F-074-1 leading-dash argv-value family (closed AT THE WRAPPER boundary by
- the --opt=value/-- convention; the CLI's own direct argv exposure stays routed),
- F-073-6, F-075-3/F-076-1..4 (the substrate grammar owner's slice, now joined by
- F2-078-2), F-075-5.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: b6e3f7452e62a209fe33a355bae4d10d4b6a439c5d2811c5ca34ada322d7b00a
- reviewed_diff_sha256: 42fcff79a5ffc0b71fab592ea7c536d06a662d1df237370012412ff59bb99bf8
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 10

## Assembly
- sheet sha256 (of the content above, excluding this line): 7e18c702a336952039f84092b6381b0ce8bfe787d1ef7dfee9c3a70559801f3b
