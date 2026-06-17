# Goal4486 V3.0 M90 RT-DBSCAN Self-Query Count-Threshold Optimization

Status: complete, evidence-backed, not a broad automatic-route promotion.

## What Changed

M90 adds a generic OptiX primitive:

- native ABI: `rtdl_optix_write_prepared_fixed_radius_count_threshold_3d_self_device_outputs`
- Python wrapper: `PreparedOptixFixedRadiusCountThreshold3D.write_device_count_threshold_self_columns`
- partner adapter: `fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns`

The primitive is app-agnostic. It is still only a prepared 3-D fixed-radius
count-threshold device-column producer. The only special assumption is generic
self-query: query points are the same prepared point set as the search scene.
That is a common fixed-radius workload shape, not RT-DBSCAN-specific logic.

RT-DBSCAN's predicate direct-status compact-signature route now uses this
self-query producer, so the native run reuses the prepared device search buffer
as the query buffer instead of rebuilding and uploading host query points.

## Evidence

Pod: NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20,475 MiB.

Artifacts:

- `docs/reports/goal4486_v3_0_m90_rtdbscan_self_query_count_threshold_1m_2026-06-17.json`
- `docs/reports/goal4486_v3_0_m90_rtdbscan_self_query_count_threshold_1m_2026-06-17.jsonl`
- `build/goal4486_m90_predicate_direct_status_self_query_smoke.json`

Validation:

- native OptiX rebuild passed with the new exported symbol;
- focused unit test passed locally and on the pod;
- old host-query and new self-query count-threshold columns matched on a pod smoke;
- RT-DBSCAN 4k app smoke matched CPU reference;
- 1M focused matrix matched all M89 signatures.

The new metadata consistently records:

- `threshold_adapter = fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns`
- `threshold_transfer_mode = prepared_device_search_points_self_count_threshold_columns`
- `threshold_query_source = prepared_search_points_self_query_device`
- `threshold_host_query_point_upload_avoided = true`

## 1M Focused Matrix

Comparison baseline is Goal4485/M89 predicate direct-status on the same 1,048,576-point profiles. For one-shot rows, the compared metric is prepare-plus-replay. For warmed replay rows, the compared metric is measured replay elapsed.

| Dataset | Protocol | M89 metric | M90 metric | M90 vs M89 | Signature |
| --- | ---: | ---: | ---: | ---: | --- |
| clustered3d | one-shot | 11.362s | 9.946s | 1.14x faster | match |
| clustered3d | warmed replay | 5.773s | 5.366s | 1.08x faster | match |
| road3d | one-shot | 10.425s | 5.119s | 2.04x faster | match |
| road3d | warmed replay | 5.254s | 2.073s | 2.53x faster | match |
| ngsim_dense | one-shot | 6.509s | 4.466s | 1.46x faster | match |
| ngsim_dense | warmed replay | 1.243s | 1.307s | 0.95x, slight loss | match |

## Attributable Kernel-Side Effect

The directly attributable change is the count-threshold run, not the whole
direct-status signature phase.

| Dataset | M89 count-threshold run | M90 self-query count-threshold run | Reduction |
| --- | ---: | ---: | ---: |
| clustered3d | 2.338s | 0.340s | 6.88x faster |
| road3d | 2.200s | 0.164s | 13.45x faster |
| ngsim_dense | 2.212s | 0.230s | 9.61x faster |

This is the core M90 result: RTDL was still doing unnecessary host query
repacking/upload for a self-query fixed-radius workload. M90 removes that
overhead while preserving the generic primitive boundary.

## Interpretation

M90 closes a real V3 optimization debt. The optimized path still uses RTDL's
intended design: a generic RT primitive emits device columns, then a CuPy partner
continuation performs the predicate direct-status compact signature.

Do not overclaim the warmed-replay rows. In the app protocol, measured replay
iterations reuse threshold columns, so their elapsed time is dominated by the
CuPy direct-status signature. The warmed-replay movement in this packet is
useful evidence for the route, but the architecturally attributable M90 win is
the count-threshold run reduction and the one-shot route improvement.

## Decision

Keep predicate direct-status CuPy as the explicit measured compact-summary route
for 524k/1M RT-DBSCAN-shaped profiles. M90 updates the implementation and
guidance from generic prepared count-threshold device columns to generic
prepared self-query count-threshold device columns.

Remaining debt:

- direct-status prepare still rebuilds CuPy partition columns separately from
  OptiX scene preparation;
- warmed replay is now mostly CuPy direct-status signature time, not RT count
  time;
- route/partner selection remains explicit and should not be hidden behind an
  automatic dispatcher.
