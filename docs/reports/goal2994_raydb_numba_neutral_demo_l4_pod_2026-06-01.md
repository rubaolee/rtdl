# Goal2994 - RayDB-Style v2.6 Numba Neutral Demonstrator L4 Pod Result

Date: 2026-06-01

## Purpose

Goal2994 records the first benchmark-app demonstrator for v2.6 after the
Goal2993 generic Numba neutral-handoff checkpoint. The app is the RayDB-style grouped aggregate benchmark, and the demonstrated mode is `avg_as_sum_count`.

This is deliberately a post-RT continuation demonstrator: the app supplies
generic `group_ids` and `values` columns that represent app-lowered RT results,
then RTDL routes the continuation through user-selected `partner="numba"`.

## Pod

- Host: `d82fc5502d11`
- GPU: `NVIDIA L4`
- Source commit: `43f0c63791b1dd078c4a4c66f69fa8e45b709839`
- Artifact:
  `docs/reports/goal2994_raydb_numba_neutral_demo_l4_pod_2026-06-01.json`
- Toolchain target:
  `.pydeps_v26_numba_cuda/numba_cuda/numba/cuda/__init__.py`
- `NUMBA_CUDA_USE_NVIDIA_BINDING=1`
- `NUMBA_CUDA_ENABLE_MINOR_VERSION_COMPATIBILITY=1`

## Result

The large L4 pod run passed:

- Rows: `1,000,000`
- Groups: `4,096`
- Mode: `avg_as_sum_count`
- Operations: `segmented_sum_f64`, `segmented_count_i64`
- Continuation path: `v2_6_numba_neutral_front_door`
- Neutral handoff validation: `accept`
- Counts match CPU: `true`
- Sums match CPU: `true`
- Maximum sum absolute error: `6.821210263296962e-13`
- Runner elapsed time: `1.235245008021593s`
- Legacy torch carrier used: `false`
- Torch conversion used: `false`

This proves that a benchmark-app path can use RTDL's generic Numba front doors
through the v2.6 neutral handoff. It also proves that the RayDB app code keeps
query encoding and result interpretation in Python while the generic partner
continuation sees only group ids and numeric payload values.

## Boundary

Goal2994 does not claim full RayDB paper reproduction, RT traversal replacement,
RT-core speedup, public speedup, whole-app speedup, true zero-copy, Numba
speedup, release readiness, automatic partner selection, automatic Triton
selection, or app-specific native engine behavior.

The result is correctness/conformance evidence for an app-level Numba
continuation path. Same-contract performance claims remain blocked until a
proper baseline comparison is designed and reviewed.

## Next

The next v2.6 step is either:

1. Add Numba segmented min/max so the RayDB-style `min`, `max`, and full
   `count/sum/min/max/avg` family can use the same user-selected Numba path; or
2. Pick a second benchmark app whose required continuation is already covered
   by segmented count/sum.

The better next engineering target is Numba segmented min/max because it closes
the obvious gap exposed by this app without adding app-specific engine logic.
