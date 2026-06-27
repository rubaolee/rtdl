# Goal 750: OptiX Interval-Local Intersection Audit

## Verdict

ACCEPT. The Goal748 robot short-ray blocker exposed a broader source pattern: custom OptiX intersection programs must not report a fixed `t` outside the current ray interval. One additional risky site was found and fixed for segment/polygon hitcount.

## Root Rule

For custom primitives, `optixReportIntersection(t, kind)` only reports a hit if `t` lies inside the current ray interval. If the raygen normalizes direction and sets `tmax` to a short world-space length, a hardcoded `0.5f` can drop valid hits.

For pure any-hit/count semantics where exact hit distance is not used, it is safe to report an interval-local `t`:

```cpp
float hit_t = optixGetRayTmin() + 1.0e-6f;
if (hit_t > optixGetRayTmax()) hit_t = optixGetRayTmax();
optixReportIntersection(hit_t, 0u);
```

## Fixed Sites

| Site | Old behavior | Risk | Action |
|---|---|---|---|
| `__intersection__rayhit_isect` | `optixReportIntersection(0.5f, 0u)` | Drops short 2D ray/triangle any-hit rays, including robot vertical edges. | Fixed in Goal748. |
| `__intersection__segpoly_isect` | `optixReportIntersection(0.5f, 0u)` | Drops short segment/polygon hitcount segments because raygen uses unit direction and `tmax=len`. | Fixed in Goal750. |

## Regression Tests

Robot / ray-triangle:

- `tests.goal637_optix_native_any_hit_test.Goal637OptixNativeAnyHitTest.test_optix_native_any_hit_2d_matches_cpu_for_short_rays`
- `tests.goal671_optix_prepared_anyhit_count_test.Goal671OptixPreparedAnyHitCountNativeTest.test_prepared_anyhit_count_matches_cpu_for_short_rays`

Segment/polygon:

- `tests.goal110_segment_polygon_hitcount_closure_test.Goal110OptixClosureTest.test_optix_matches_python_reference_for_short_segment_inside_polygon`

## Linux Native Validation

On `lestat-lx1`, after rebuilding OptiX with:

```bash
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc
```

the focused native suite passed:

```text
tests.goal110_segment_polygon_hitcount_closure_test
tests.goal637_optix_native_any_hit_test
tests.goal671_optix_prepared_anyhit_count_test
17 tests OK
```

## Other Hardcoded `0.5f` Sites

| Site | Current risk read |
|---|---|
| `__intersection__lsi_isect` | Lower risk for this specific bug because LSI raygen uses unnormalized segment direction and `tmax=1.0 + pad`, so `0.5f` is interval-valid. Still worth future cleanup for consistency. |
| `__intersection__pip_isect` | Lower risk because PIP raygen uses an upward ray with `tmax=1.0e30f`; `0.5f` is interval-valid. |
| `__intersection__overlay_isect` | Lower risk for this specific bug because overlay traces polygon edges with unnormalized direction and `tmax=1.0`; `0.5f` is interval-valid. |
| `__intersection__db_scan_isect` | Lower risk because DB scan raygen uses positive `tmax` spanning the encoded z range plus padding. |

## Boundary

This audit fixes correctness hazards in native OptiX custom-intersection reporting. It does not by itself create RTX RT-core speedup evidence. RTX-class hardware validation remains required for performance claims.
