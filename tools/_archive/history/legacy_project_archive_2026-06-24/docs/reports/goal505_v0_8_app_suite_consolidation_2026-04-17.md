# Goal 505: v0.8 App Suite Consolidation

Date: 2026-04-17

Status: accepted by external AI review and Codex consensus

Version line: `v0.8` app-building over existing RTDL language features

## Purpose

Goals 502, 503, and 504 implemented three paper-derived applications using the
existing RTDL language/runtime surface. Goal505 consolidates them into a
coherent public app-building story so users see the common pattern instead of
three isolated scripts.

## Public Tutorial Added

New tutorial:

- `/Users/rl2025/rtdl_python_only/docs/tutorials/v0_8_app_building.md`

It teaches the v0.8 pattern:

1. Python prepares domain data.
2. RTDL emits reusable query rows.
3. Python reduces those rows into application answers.
4. Reusable language gaps are documented before adding new primitives.

## App Suite

| App | RTDL feature used | Python-owned work |
| --- | --- | --- |
| Hausdorff distance | `knn_rows(k=1)` | directed/undirected reduction, witness IDs, brute-force oracle |
| Robot collision screening | `ray_triangle_hit_count` | pose/link metadata, edge-ray generation, collision aggregation |
| Barnes-Hut force approximation | `fixed_radius_neighbors` | quadtree construction, opening rule, force-vector math, oracle error |

## Docs Updated

- `/Users/rl2025/rtdl_python_only/docs/tutorials/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/v0_8_app_building.md`

## Suite Test Added

New test:

- `/Users/rl2025/rtdl_python_only/tests/goal505_v0_8_app_suite_test.py`

The test verifies:

- all three apps run in process
- all three CLIs emit valid JSON
- oracle/error claims remain true
- boundary messages remain present
- the new tutorial links all three examples and records the Barnes-Hut language
  gaps

## Validation

Command:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal505_v0_8_app_suite_test tests.goal208_nearest_neighbor_examples_test tests.goal503_robot_collision_screening_app_test tests.goal504_barnes_hut_force_app_test -v
```

Result:

```text
Ran 16 tests in 0.828s
OK
```

Command:

```text
PYTHONPATH=src:. python3 examples/rtdl_feature_quickstart_cookbook.py
```

Result:

```text
feature_count = 19
hausdorff_distance_app present
robot_collision_screening_app present
barnes_hut_force_app present
```

Command:

```text
PYTHONPATH=src:. python3 -m py_compile tests/goal505_v0_8_app_suite_test.py
git diff --check
```

Result:

```text
OK
```

## Honesty Boundary

Goal505 does not claim a new RTDL language primitive or new backend capability.
It consolidates applications built over existing language features.

The Barnes-Hut tutorial explicitly records the exposed future gaps:

- tree-node inputs
- opening predicates
- vector reductions

## Verdict

Goal505 is accepted.

External AI reviews:

- Claude review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal505_claude_review_2026-04-17.md`
  - Verdict: PASS
  - Finding: the tutorial, release-facing examples, tutorial index, and suite
    tests correctly present Goals 502-504 as existing-surface app-building
    examples without claiming new language internals or backend capabilities.
- Gemini Flash review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal505_gemini_flash_review_2026-04-17.md`
  - Verdict: ACCEPT
  - Finding: the consolidation is coherent, the test validates the public
    contract, and the Barnes-Hut gaps are recorded as future pressure rather
    than shipped capability.

Codex consensus:

- `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-17-codex-consensus-goal505-v0_8-app-suite-consolidation.md`

Goal505 makes v0.8 understandable as an app-building release line rather than
a set of disconnected examples.
