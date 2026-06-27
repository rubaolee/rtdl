# Call For Review: V4 Public Surface, API, Tutorial, And Packaging Hardening

Date: 2026-06-27

Requested verdict labels:

- `approve_public_surface_hardening`
- `approve_with_required_fixes`
- `block_public_surface_until_fixed`

## Scope

Please critically review the current V4.0 public-surface hardening work after
commits:

- `3bc6d9223 Add clean V4 benchmark app recipes`
- `8c7d4a603 Clarify V4 benchmark learning path`
- `86a1098d0 Add benchmark recipes to V4 doc map`
- `7e9afff09 Limit V4 star-import public API`
- `77a756ae0 Hide V4 maintainer symbols from dir`
- `07ea16fe9 Gate runnable V4 tutorial snippets`
- `56c82df15 Gate V4 benchmark tutorial coverage`
- `a15fa6405 Gate V4 public documentation links`
- `cf9fb36b4 Gate V4 wheel candidate contents`

This is not a request to authorize broader performance claims. It is a request
to verify whether the V4.0 public user surface is now clean enough for a major
version entrypoint.

## What Changed

1. `examples/v4/benchmark_app_recipes.py` is now the clean first code path for
   learning how all 10 benchmark apps map to V4 operators.
2. `examples/current/research_benchmarks/` is presented as a maintainer matrix
   harness, not the first teaching surface.
3. `docs/public_documentation_map.md`, `examples/README.md`, root `README.md`,
   and `examples/current/research_benchmarks/README.md` now point users to the
   V4 recipe path first.
4. `rtdsl.v4.__all__` is constrained to `PUBLIC_API_SYMBOLS_V4`; internal
   goal/protocol symbols remain direct-maintainer compatibility attributes but
   are not exported through star-import.
5. `dir(rtdsl.v4)` now returns the same clean public symbol list, so REPL users
   do not see maintainer goal/protocol symbols by default.
6. Public cleanup tests now execute every public `examples/v4` entrypoint.
7. Public cleanup tests now execute every Python code block in
   `tutorials/current/` as standalone copy-paste runnable snippets.
8. Public cleanup tests now verify the benchmark tutorial and recipe planner
   cover all 10 promoted apps.
9. Public cleanup tests now verify every relative link in the public docs
   resolves.
10. Packaging tests now inspect existing V4 wheel candidates and reject docs,
    history, future provenance, examples, tutorials, or Phoenix/V3 debris in
    the wheel.

## Verification Already Run

Strict universe audit:

```powershell
py -3 scripts\v4_universe_audit.py --format json --strict-release
```

Result: `status: pass`, `public_findings: []`, `unknown_untracked_count: 0`.

Focused public gate:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.v4_goal4640_public_docs_cleanup_test
```

Result: `Ran 12 tests ... OK`.

Full V4 discovery:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest discover -s tests -p "v4*_test.py"
```

Result: `Ran 655 tests in 120.731s`, `OK (skipped=1)`.

Syntax/package sanity:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m compileall -q src examples/v4 tutorials/current scripts tests
```

Result: exit code `0`.

Wheel content check:

- `dist/goal4722_v4_release_candidate/rtdl_source_tree-4.0.0-py3-none-any.whl`
- `dist/goal4758_v4_release_candidate/rtdl_source_tree-4.0.0-py3-none-any.whl`

Both contain package files only, no `docs/`, `history/`, `future/`,
`examples/`, `tutorials/`, `docs/reviews`, or `phoenix_v3` paths; metadata
reports `Name: rtdl-source-tree` and `Version: 4.0.0`.

## Please Check

1. Is the first-time user path clean enough now?
2. Do the docs still leak internal process language, AI names, goal identifiers,
   review-debt wording, or old-version confusion?
3. Is `examples/v4/benchmark_app_recipes.py` a sufficient clean bridge from the
   V4 programming model to the 10 benchmark apps?
4. Is it acceptable that the full benchmark harness remains under
   `examples/current/research_benchmarks/` as maintainer machinery, provided
   its README clearly routes learners to the clean V4 recipe first?
5. Is `rtdsl.v4.__all__` plus `dir(rtdsl.v4)` clean enough as the public Python
   API surface while direct-maintainer compatibility symbols remain importable?
6. Are the runnable-snippet, link, example, strict-audit, and wheel-content
   gates sufficient to prevent the same public-surface regression?
7. What P0/P1 fixes, if any, are still required before considering the V4.0
   public documentation/API surface acceptable?

## Non-Authorization

This review must not authorize:

- broad V4-over-V2.14 or V4-over-V3 speedup wording;
- whole-app high-performance wording across all benchmark apps;
- Tier-3 arbitrary callback support;
- C ABI, embedding, or non-Python host claims;
- true external zero-copy claims;
- app-identity native kernels.

The only requested decision is whether the V4 public docs/API/examples/package
surface is now clean enough, or what exact fixes still block it.
