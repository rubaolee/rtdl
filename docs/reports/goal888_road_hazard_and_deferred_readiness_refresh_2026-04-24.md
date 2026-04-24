# Goal888 Road Hazard And Deferred Readiness Refresh

Date: 2026-04-24

## Result

Goal888 adds a local gate for the road-hazard app's explicit native OptiX
segment/polygon path:

```bash
scripts/goal888_road_hazard_native_optix_gate.py
```

The gate compares CPU Python reference output with `--backend optix
--optix-mode native` output and supports strict RTX validation. On local macOS,
missing OptiX is recorded as an unavailable backend, not as a correctness
failure.

Goal888 also refreshes app readiness metadata:

- `road_hazard_screening`: `needs_real_rtx_artifact`
- `segment_polygon_hitcount`: `needs_real_rtx_artifact`
- `polygon_pair_overlap_area_rows`: `needs_real_rtx_artifact`
- `polygon_set_jaccard`: `needs_real_rtx_artifact`

These apps are still not active RTX claim entries. They are deferred because
local gate/phase packaging exists and the next missing evidence is a real RTX
artifact plus review.

## Manifest Impact

The RTX manifest now has:

- active entries: `5`
- deferred entries: `11`
- baseline contracts: `16`

The new deferred entry is:

```text
road_hazard_screening / road_hazard_native_summary_gate
```

It uses compact summary output and the explicit native segment/polygon OptiX
mode. It does not promote default road-hazard app behavior or a full GIS/routing
speedup claim.

## Same-Pod Batch

The runbook and cloud start packet now include all 11 deferred targets:

- `service_coverage_gaps`
- `event_hotspot_screening`
- `road_hazard_screening`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `hausdorff_distance`
- `ann_candidate_search`
- `facility_knn_assignment`
- `barnes_hut_force_app`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

Dry-run result:

```text
status=ok, include_deferred=true, only_count=11
```

## Boundary

This goal makes road hazard and the remaining deferred apps ready for batched
RTX evidence collection. It does not authorize public RTX speedup claims.

Claims still require:

- real RTX artifacts,
- correctness parity,
- phase separation,
- baseline review,
- independent review.

## Verification

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal888_road_hazard_native_optix_gate_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal822_rtx_cloud_manifest_claim_boundary_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test \
  tests.goal887_prepared_decision_phase_profiler_test
```

Result: `33 tests OK`.

Pre-cloud gate:

```bash
PYTHONPATH=src:. python3 scripts/goal824_pre_cloud_rtx_readiness_gate.py \
  --output-json docs/reports/goal888_pre_cloud_readiness_after_road_hazard_gate_2026-04-24.json
```

Result: `valid: true`.

