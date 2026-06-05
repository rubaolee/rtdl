# Goal3443 Spatial RayJoin Overlay Active-Count Device Default

**Date:** 2026-06-05
**Status:** implemented and pod-validated
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

Pod artifact:

- `docs/reports/goal3443_spatial_rayjoin_overlay_active_count_device_default_pod_2026-06-05.json`
- `docs/reports/goal3443_spatial_rayjoin_overlay_active_count_device_default_pod_2026-06-05.stdout`

Pod result on `NVIDIA RTX A5000, 580.126.09`, commit
`da48c460438b09fa7ae59c7976570ccdd11738f0`:

| Subroute | Stable count | Warm median seconds | Notes |
| --- | ---: | ---: | --- |
| PIP candidate columns | `47,570` candidates / `47,262` rows | `0.021088` candidate, `0.001277` CuPy refine | Cold first iteration recorded separately |
| LSI dense count | `101,407` intersections | `0.002361` | Cold first iteration recorded separately |
| Overlay active count default | `4,543` active pairs | `0.005458` | Uses `active_count_device_continuation_sec`; first iteration `0.327948s` paid cold module/first-use cost |

The overlay default route now reports native timing mode
`active_count_device_continuation`, and only the scalar active count is copied
back. All claim-boundary flags in the artifact remain false.
