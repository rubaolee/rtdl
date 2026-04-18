# Goal 513: Public Example Smoke Gate

Date: 2026-04-17

Status: accepted with 3-AI consensus

## Scope

Goal513 adds a public-example smoke gate for the examples that a new RTDL user
is most likely to run from the front page, tutorials, and examples index. The
goal is to catch stale command lines, broken JSON output, and v0.8 app-example
regressions before release-facing docs are treated as ready.

## Public Examples Covered

- `/Users/rl2025/rtdl_python_only/examples/rtdl_hello_world.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_segment_polygon_hitcount.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_feature_quickstart_cookbook.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_graph_bfs.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_graph_triangle_count.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_db_conjunctive_scan.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_db_grouped_count.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_db_grouped_sum.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_v0_7_db_app_demo.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_v0_7_db_kernel_app_demo.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_hausdorff_distance_app.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_robot_collision_screening_app.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_barnes_hut_force_app.py`

## Changes Made

- Added `/Users/rl2025/rtdl_python_only/tests/goal513_public_example_smoke_test.py`.
- The test runs the public example commands as subprocesses with
  `PYTHONPATH=src:.`, matching the local source-tree usage pattern.
- The test accepts the existing public JSON output contracts instead of forcing
  older examples to add an `app` field.

## Test Coverage Added

The new test checks:

- the hello-world example prints the expected text
- all front-page portable examples run without subprocess failure
- all JSON examples emit parseable JSON with either app-style or row-style output
- the v0.8 Hausdorff and robot examples report oracle agreement
- the v0.8 Barnes-Hut example reports its bounded one-level approximation and
  candidate row count
- the feature quickstart cookbook includes the three v0.8 app-building recipes

## Validation

Command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal513_public_example_smoke_test tests.goal512_public_doc_smoke_audit_test -v
```

Result: `Ran 6 tests`, `OK`.

Command:

```bash
PYTHONPATH=src:. python3 -m py_compile tests/goal513_public_example_smoke_test.py && git diff --check
```

Result: passed.

## Current Verdict

Goal513 is accepted. The public-example smoke gate now verifies the
front-page/tutorial/example commands most likely to be run by new users.

## AI Review Consensus

- Claude review: `PASS`; the gate covers the scoped examples, preserves
  existing app-style and row-style JSON output contracts, and checks the v0.8
  app oracle/boundary fields. Claude noted that the subprocess environment
  should augment `os.environ` instead of replacing it; that fragility was fixed
  after review.
- Gemini Flash review: `ACCEPT`; the gate runs the front-page portable
  examples, parses JSON without forcing an `app` key, and validates the v0.8
  app oracle/boundary outputs.
- Codex conclusion: `ACCEPT`; Goal513 adds a narrow, useful public-example
  smoke gate after Goal512's public-doc smoke audit.
