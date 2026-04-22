# Goal701 Robot Collision Compact Output

Date: 2026-04-21

Verdict: ACCEPT as app-interface performance polish for the current OptiX
flagship candidate.

## Scope

Goal701 updates:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_robot_collision_screening_app.py`
- `/Users/rl2025/rtdl_python_only/tests/goal701_robot_collision_compact_output_test.py`
- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`
- `/Users/rl2025/rtdl_python_only/docs/application_catalog.md`
- `/Users/rl2025/rtdl_python_only/docs/app_engine_support_matrix.md`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/app_support_matrix.py`

## User-Facing Change

The robot collision app now accepts:

```bash
--output-mode full
--output-mode pose_flags
--output-mode hit_count
```

Default `full` mode is backwards compatible and returns witness rows, enriched
edge rows, pose summaries, oracle data, and full app details.

`pose_flags` returns only compact pose collision flags and colliding pose IDs.

`hit_count` returns only a compact hit-edge count and oracle count.

The existing OptiX-only:

```bash
--optix-summary-mode prepared_count
```

continues to return a native scalar hit-edge count through prepared OptiX
ray/triangle any-hit.

## Performance Meaning

This reduces Python/JSON app-interface row volume when users only need compact
summaries. It makes the app easier to use as an NVIDIA RT-core validation
target because the row-heavy and compact-summary modes are explicit.

## Honesty Boundary

Post-Goal753 update: RTDL now has a prepared OptiX pose-flag ABI for this app
summary shape. In row mode, compact outputs still compute summaries from
emitted rows. `prepared_pose_flags` returns pose-level collision flags only;
edge witnesses and hit-ray IDs still require row mode.

This goal also does not claim RTX speedup. RTX-class cloud validation is still
required before public performance claims.

## Verification

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal701_robot_collision_compact_output_test \
  tests.goal691_optix_robot_summary_profiler_test \
  tests.goal649_app_rewrite_anyhit_reduce_rows_test \
  tests.goal503_robot_collision_screening_app_test \
  tests.goal690_optix_performance_classification_test \
  tests.goal687_app_engine_support_matrix_test

PYTHONPATH=src:. python3 -m py_compile \
  examples/rtdl_robot_collision_screening_app.py \
  tests/goal701_robot_collision_compact_output_test.py

git diff --check
```

Result: `23` focused tests OK, `py_compile` OK, `git diff --check` OK.
