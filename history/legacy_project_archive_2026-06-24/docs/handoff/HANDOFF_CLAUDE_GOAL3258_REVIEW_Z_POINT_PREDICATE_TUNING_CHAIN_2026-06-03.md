# Handoff: Claude Review Of Goal3256-3258 Z-Point Predicate Tuning Chain

Date: 2026-06-03

Please perform a read-only independent review of the Goal3256-3258 native
closed-shape tuning chain for the RayJoin PIP benchmark.

## Required Output

Write the review to:

`docs/reviews/goal3259_claude_review_goal3256_3258_z_point_predicate_tuning_chain_2026-06-03.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

## Context

Goal3255 showed that the existing generic OptiX AABB point-containing-box
primitive is fast and selective on the same RayJoin PIP slice:

- AABB point_contains: `0.071144 ms`, candidate count `1542`.
- Exact closed-shape device-filtered count: `0.780968 ms`, exact positive
  count `1430`.

Goals 3256-3258 then tuned the generic point/closed-shape path:

- Goal3256 added opt-in `RTDL_OPTIX_POINT_PRIMITIVE_QUERY_AXIS=z_point`.
- Goal3257 fused boundary detection and ray-casting into one device edge loop.
- Goal3258 replaced the per-edge `sqrtf` boundary check with squared-cross
  comparison.

Best measured same-slice PIP row now:

- RayJoin PIP median: `0.208473 ms`.
- RTDL PIP median: `0.351587 ms`.
- Ratio: `1.686x` slower.
- RTDL count: `1430`.

This is an improvement from `4x+` slower, but it is not a release claim and not
an `RTDL beats RayJoin` claim.

## Files To Inspect

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `tests/goal3256_closed_shape_z_point_probe_mode_test.py`
- `tests/goal3257_closed_shape_single_pass_predicate_test.py`
- `tests/goal3258_closed_shape_squared_boundary_predicate_test.py`
- `tests/goal3258_closed_shape_z_point_predicate_tuning_chain_test.py`
- `docs/reports/goal3255_rayjoin_pip_aabb_broadphase_probe_2026-06-03.md`
- `docs/reports/goal3258_closed_shape_z_point_predicate_tuning_chain_2026-06-03.md`
- `docs/reports/goal3256_closed_shape_z_point_probe_pod_2026-06-03.json`
- `docs/reports/goal3256_rayjoin_z_point_same_slice_pod_2026-06-03.json`
- `docs/reports/goal3257_closed_shape_z_point_single_pass_probe_pod_2026-06-03.json`
- `docs/reports/goal3257_rayjoin_z_point_single_pass_same_slice_pod_2026-06-03.json`
- `docs/reports/goal3258_closed_shape_z_point_squared_boundary_probe_pod_2026-06-03.json`
- `docs/reports/goal3258_rayjoin_z_point_squared_boundary_same_slice_pod_2026-06-03.json`

## Questions To Answer

1. Is the `z_point` axis specialization generic and opt-in, with default
   vertical behavior preserved?
2. Does the native code avoid RayJoin/app-specific names or app-shaped ABI?
3. Does the single-pass predicate preserve inclusive boundary behavior and exact
   point-in-shape semantics at the intended float32 predicate boundary?
4. Is replacing `fabs(cross) <= eps * sqrt(len2)` with
   `cross * cross <= eps * eps * len2` mathematically equivalent enough for the
   existing predicate tolerance?
5. Do the pod artifacts support the stated performance chain:
   `0.548579 ms` -> `0.396991 ms` -> `0.351587 ms` same-slice RTDL PIP,
   with count `1430` preserved?
6. Are all claim boundaries preserved? Do not authorize release, public
   speedup, broad RT-core speedup, true zero-copy, `RTDL beats RayJoin`, or
   RayJoin paper reproduction claims.
7. What is the best next engineering target: promote `z_point` to a first-class
   public mode, make it the default after more coverage, add a prepared-edge
   layout, or explore warp-cooperative predicate evaluation?

## Validation To Run If Practical

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3258_closed_shape_z_point_predicate_tuning_chain_test `
  tests.goal3258_closed_shape_squared_boundary_predicate_test `
  tests.goal3257_closed_shape_single_pass_predicate_test `
  tests.goal3256_closed_shape_z_point_probe_mode_test `
  tests.goal3255_rayjoin_pip_aabb_broadphase_probe_pod_evidence_test
```

This is a review task only. Do not edit source files except for the requested
review file.
