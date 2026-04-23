# Goal844 Robot Oracle Parallelization

## Scope

Reduce the operational cost of the remaining active robot baseline artifacts by parallelizing the exact CPU pose-flag oracle on Linux, without changing semantics.

## What Changed

- Updated:
  - `scripts/goal839_robot_pose_count_baseline.py`
- Expanded tests:
  - `tests/goal839_local_baseline_collectors_test.py`

## Design

- The exact CPU pose-flag oracle remains the reference implementation.
- On Linux only, when the pose count is large enough, the collector now uses process-level parallelism with `multiprocessing.get_context("fork")`.
- Each worker evaluates a disjoint ray slice using the same exact `rt.ray_triangle_pose_flags_cpu(...)` logic.
- The parent process merges worker outputs with boolean OR over pose indices.
- This preserves exact semantics because a pose is colliding iff any worker observes a hit for any ray belonging to that pose.

## Boundaries

- No public app behavior changed.
- No baseline artifact schema changed.
- No claim boundary changed.
- Non-Linux hosts still default to the original single-process exact path.

## Verification

- `PYTHONPATH=src:. python3 -m unittest -v tests.goal839_local_baseline_collectors_test tests.goal843_linux_active_baseline_batch_test tests.goal842_postgresql_db_prepared_baseline_test`
- `python3 -m py_compile scripts/goal839_robot_pose_count_baseline.py tests/goal839_local_baseline_collectors_test.py`
- `git diff --check`

Result: all focused checks passed.

## Operational Impact

This change is specifically intended to make the remaining Linux robot baseline collection operationally feasible at the required Goal835 scale.
