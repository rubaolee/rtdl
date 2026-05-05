# Goal1303: Robot Prepared Count Generic ANY_HIT Migration

Date: 2026-05-05

## Purpose

Goal1303 migrates `robot_collision_screening / prepared_count` onto the v1.5
generic prepared ray/triangle primitive:

```text
ANY_HIT + COUNT_HITS
```

This is an internal v1.5 migration slice. It does not migrate
`prepared_pose_flags`, because pose flags require grouped app-specific
reduction that is not yet part of the generic primitive ABI.

## Change

`prepared_count` now calls:

```text
run_generic_prepared_ray_triangle_any_hit_count(...)
```

The app payload still reports `native_continuation_backend` as
`optix_prepared_any_hit_count`, and `prepared_summary` now exposes:

```text
generic_primitive = ANY_HIT
summary_primitive = COUNT_HITS
```

## Local Verification

Passed locally:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal953_robot_native_continuation_metadata_test \
  tests.goal701_robot_collision_compact_output_test \
  tests.goal691_optix_robot_summary_profiler_test \
  tests.goal1288_v1_5_generic_anyhit_count_test \
  tests.goal1290_v1_5_generic_prepared_anyhit_count_test
```

Result:

```text
Ran 24 tests in 1.555s

OK
```

Passed locally:

```text
PYTHONPATH=src:. python3 -m py_compile \
  examples/rtdl_robot_collision_screening_app.py \
  tests/goal953_robot_native_continuation_metadata_test.py
```

`git diff --check` passed.

## Next Pod Action

Run the migrated OptiX prepared-count path on the active RTX pod:

```text
PYTHONPATH=src:. python3 examples/rtdl_robot_collision_screening_app.py \
  --backend optix --optix-summary-mode prepared_count \
  --pose-count 4096 --obstacle-count 1024 --skip-validation
```

## Boundary

This proves the scalar hit-edge count path uses the generic prepared
ray/triangle `ANY_HIT + COUNT_HITS` primitive. It does not claim pose-level
flags, continuous collision detection, full robot kinematics, mesh collision,
whole-app acceleration, or public NVIDIA speedup wording.
