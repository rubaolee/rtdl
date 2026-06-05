# Goal3446 v2.8 Runtime-Gap Refresh After RayJoin Active-Count Device Default

**Date:** 2026-06-05  
**Status:** implemented  
**Scope:** v2.8 benchmark-runtime gap metadata refresh after Goals3441-3443

## Purpose

Goal3441-3443 changed the status of the Spatial RayJoin overlay scalar-summary
route. Before this chain, the v2.8 runtime-gap row correctly said overlay
active-count summaries were prepared/reusable but still slow and host-heavy.
After the chain, that statement is stale:

- Goal3441 measured the old host route and showed the time was not OptiX
  traversal dominated. The measured native phases were mostly host-side flag
  download, CPU containment, host active scan, and orchestration.
- Goal3442 added a generic device-side active-count continuation over generic
  shape-pair relation flags, copying back only the scalar count.
- Goal3443 promoted that device continuation to the Spatial RayJoin app-layer
  default while keeping `run_packed_left_host_exact(...)` as the explicit
  oracle/debug route.

This goal updates the v2.8 runtime-gap map so the project no longer treats
overlay scalar active count as the remaining weak spot.

## Metadata Update

| Field | Update |
| --- | --- |
| `current_best_path` | Adds that generic device-side active-count continuation is now the default overlay scalar-summary route. |
| `current_bottleneck` | Distinguishes the solved scalar active-count route from the still-open full relation-row / richer grouped continuation problem. |
| `evidence_refs` | Adds `Goal3441`, `Goal3442`, and `Goal3443` to the Spatial RayJoin row. |

## Current RayJoin Interpretation

The updated Spatial RayJoin row now says:

- PIP exact continuation has instance-aware candidate columns and prepared CuPy
  refinement evidence.
- LSI has reusable prepared grouped/dense count evidence.
- Overlay scalar active count has a generic device continuation and is the app
  default.
- The remaining hard gap is not scalar count. It is full overlay relation-row output,
  richer parity/count grouping over resident row streams, and boundary-witness
  ownership at serious scale.

## Evidence

The pod artifacts remain claim-bounded:

- Goal3441 host diagnostic: median about `0.147s` and phase timing showing the
  old host bottleneck.
- Goal3442 opt-in device continuation: host count `[4543, 4543, 4543, 4543]`
  matched device count `[4543, 4543, 4543, 4543]`, with warm median about
  `0.00644s`.
- Goal3443 default route: overlay active count stayed `4543` and warm median
  was about `0.00546s`, with cold first-use cost disclosed.

## Boundary

This is a metadata/status refresh, not a release action. It does not authorize:

- v2.8 release;
- public speedup wording;
- RayJoin paper reproduction claims;
- RTDL-beats-RayJoin claims;
- broad RT-core speedup claims;
- true-zero-copy claims;
- app-specific native engine logic.

The native implementation remains a generic shape-pair relation plus generic
active-count continuation; Spatial RayJoin semantics stay in the app/reference
benchmark layer.

## Validation

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3446_v2_8_runtime_gap_after_rayjoin_active_count_device_default_test tests.goal3443_spatial_rayjoin_overlay_active_count_device_default_test tests.goal3105_v2_8_benchmark_runtime_gap_map_test
py -3 -m py_compile src\rtdsl\v2_8_benchmark_runtime_gap.py tests\goal3446_v2_8_runtime_gap_after_rayjoin_active_count_device_default_test.py
```

The focused test checks the updated Spatial RayJoin row, the Goal3443 pod
artifact if present, and the claim-boundary wording in this report.
