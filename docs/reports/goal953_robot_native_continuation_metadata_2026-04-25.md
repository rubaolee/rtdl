# Goal 953: Robot Native Continuation Metadata

Date: 2026-04-25

## Scope

Goal953 normalizes robot collision screening payload metadata with the
native-continuation convention used by the other v1.0 app-polish goals.

The robot app already had prepared OptiX native summary paths:

- `prepared_count`: native scalar hit-edge count.
- `prepared_pose_flags`: native pose-level collision flags.

This goal makes those paths explicit in the public payload and docs.

## Code Changes

- `examples/rtdl_robot_collision_screening_app.py`
  - Prepared OptiX count path now reports:
    - `native_continuation_active: True`
    - `native_continuation_backend: "optix_prepared_any_hit_count"`
  - Prepared OptiX pose-flag path now reports:
    - `native_continuation_active: True`
    - `native_continuation_backend: "optix_prepared_pose_flags"`
  - Row-mode paths now explicitly report:
    - `native_continuation_active: False`
    - `native_continuation_backend: "none"`

- `tests/goal953_robot_native_continuation_metadata_test.py`
  - Verifies prepared count metadata.
  - Verifies prepared pose-flag metadata.
  - Verifies row-mode full/pose_flags/hit_count outputs do not overstate native
    continuation.

## Documentation Updates

- `docs/application_catalog.md`
- `docs/app_engine_support_matrix.md`
- `examples/README.md`
- `src/rtdsl/app_support_matrix.py`

The docs now distinguish compact row-output modes from prepared OptiX native
continuation:

- `--output-mode hit_count` / `pose_flags` on row backends reduces payload size
  but still summarizes emitted rows.
- `--optix-summary-mode prepared_count` / `prepared_pose_flags` uses native
  prepared OptiX continuation and avoids per-ray row materialization.

## Verification

Focused test gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal953_robot_native_continuation_metadata_test \
  tests.goal701_robot_collision_compact_output_test \
  tests.goal736_robot_collision_embree_scaled_test \
  tests.goal671_optix_prepared_anyhit_count_test \
  tests.goal803_rt_core_app_maturity_contract_test -v
```

Result:

```text
Ran 34 tests in 0.445s
OK (skipped=6)
```

The skips are optional native OptiX-library or numpy availability checks on
this Mac. Portable/mocked prepared OptiX tests passed.

Additional checks:

- `py_compile` passed for touched Python files.
- `git diff --check` passed for touched robot files.

## Boundaries

Goal953 does not claim:

- Full robot-planning acceleration.
- Continuous collision detection.
- Full mesh collision engine behavior.
- Edge-level witness acceleration beyond the existing row mode.
- New public RTX speedup evidence.
