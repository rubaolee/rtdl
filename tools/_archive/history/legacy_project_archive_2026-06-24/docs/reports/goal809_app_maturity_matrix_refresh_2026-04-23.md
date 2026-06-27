# Goal809 App Maturity Matrix Refresh

## Result

Goal809 refreshes the app support and RT-core maturity matrices after Goals 807 and 808.

The matrices now state that segment/polygon native OptiX mode is explicitly exposed, but still gated and not yet a public NVIDIA RT-core performance claim.

## What Changed

- Updated `/Users/rl2025/rtdl_python_only/src/rtdsl/app_support_matrix.py`.
- Updated `/Users/rl2025/rtdl_python_only/docs/app_engine_support_matrix.md`.
- Road hazard now records that OptiX has explicit `auto|host_indexed|native` mode selection, but native mode remains gated.
- Segment/polygon hit count now records that explicit native mode exists and must pass Goal807 strict gating.
- Segment/polygon any-hit rows now records the important split: compact flags/counts can request native hit-count mode, but pair-row native output does not exist yet.

## Boundary

No maturity status was promoted to `rt_core_ready`.

The only apps currently `rt_core_ready` remain:

- `outlier_detection`
- `dbscan_clustering`
- `robot_collision_screening`

## Verification

Completed:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal803_rt_core_app_maturity_contract_test tests.goal690_optix_performance_classification_test tests.goal705_optix_app_benchmark_readiness_test tests.goal808_segment_polygon_app_native_mode_propagation_test -v
python3 -m py_compile src/rtdsl/app_support_matrix.py
git diff --check
```

Result: 22 tests OK, `py_compile` OK, and `git diff --check` OK.
