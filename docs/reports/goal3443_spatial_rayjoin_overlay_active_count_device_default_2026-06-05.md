# Goal3443 Spatial RayJoin Overlay Active-Count Device Default

**Date:** 2026-06-05
**Status:** implemented; pod artifact pending
**Scope:** app-layer reference-route default for the prepared overlay active-count workload

## Purpose

Goal3442 proved that the generic shape-pair active-count device continuation
matches the existing host exact path on the available pod benchmark input and
reduces warm repeated active-count time from about `0.144s` to about `0.00644s`.

Goal3443 promotes that opt-in path to the default app-layer reference route for
`PreparedRayJoinOptixShapePairActiveCount.run_packed_left(...)` and
`prepared.run(...)`.

## What Changed

| File | Operation |
| --- | --- |
| `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` | `run_packed_left(...)` now delegates to `run_packed_left_device_continuation(...)`; the old host path is preserved as `run_packed_left_host_exact(...)`. |
| `scripts/goal3438_spatial_rayjoin_prepared_subroute_reuse_probe.py` | Accepts either old host phase timing or the new device-continuation phase timing when rerun. |
| `scripts/goal3441_shape_pair_active_count_phase_timing_probe.py` | Explicitly calls `run_packed_left_host_exact(...)` because Goal3441 is the host full-buffer diagnostic. |
| `scripts/goal3442_shape_pair_active_count_device_continuation_probe.py` | Explicitly compares `run_packed_left_host_exact(...)` against `run_packed_left_device_continuation(...)`. |
| `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md` | Documents the device-continuation default and the host-exact oracle method. |

## Boundary

This is an app-layer default change over a generic native primitive. The native
engine still sees generic shape-pair relation flags and generic active-count
continuation only. This report does not authorize release, public speedup,
RayJoin reproduction, RT-core speedup, whole-app speedup, or true zero-copy
claims.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3443_spatial_rayjoin_overlay_active_count_device_default_test tests.goal3442_shape_pair_active_count_device_continuation_test tests.goal3438_spatial_rayjoin_prepared_subroute_reuse_test
py -3 -m py_compile examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py scripts/goal3438_spatial_rayjoin_prepared_subroute_reuse_probe.py scripts/goal3441_shape_pair_active_count_phase_timing_probe.py scripts/goal3442_shape_pair_active_count_device_continuation_probe.py tests/goal3443_spatial_rayjoin_overlay_active_count_device_default_test.py
```

Pod validation should rerun the Goal3438 prepared subroute probe from current
`main` and confirm the overlay active-count route now records
`active_count_device_continuation_sec` with stable counts.
