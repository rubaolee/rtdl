# Phoenix V3 M36 Prepared-Session Step-4 Surface Ledger

Date: 2026-06-23

Status: `m36_surface_ledger_not_release`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
performance_claim_authorized: false
```

## Purpose

M36 supersedes the M33 surface ledger as the current prepared-session helper
classification. M33 and M34 remain historical records; this file is the current
machine-checked ledger after adding the grouped vector-sum/reduction helper.

This is a contract ledger, not a benchmark result.

## Current Classification

| Helper | M36 classification | Reason |
| --- | --- | --- |
| `run_fixed_radius_count_threshold_3d_self_query_prepared_session` | blocked Set-A seed | Runner call exists, but no runtime-trunk family, continuation contract, row contract, residency field, or hot-path host-materialization field is reported. It remains a possible Set-A starting shape, not a ready family. |
| `run_fixed_radius_threshold_reached_count_2d_prepared_session` | Step-4 ready by local audit | Reports runtime trunk, internal residency, no hot-path host materialization, row contract, and `threshold_reached_count_scalar_2d`. |
| `run_fixed_radius_ranked_summary_3d_prepared_session` | Step-4 ready by local audit | Reports runtime trunk, prepared-query residency, no hot-path host materialization, row contract, and `fixed_radius_ranked_summary_aggregate_3d`. |
| `run_aabb_index_query_2d_range_intersection_prepared_session` | blocked Set-B control | AABB row helper lacks runtime-trunk execution, residency, no-hot-host-stage, runtime-trunk family, continuation contract, and focused-gain gate. Metadata marks it `set_a_probe_candidate=false` and `set_b_control_candidate=true`. |
| `run_aabb_index_query_2d_count_prepared_session` | blocked Set-B control | Useful Set-B/control helper; lacks Step-3 residency facts and Step-4 continuation facts. Metadata marks it `set_a_probe_candidate=false` and `set_b_control_candidate=true`. |
| `run_aabb_index_query_2d_optix_prepared_query_set_count_prepared_session` | blocked Set-B control | Preserves an OptiX prepared-query-set shape, but is not a residency/continuation trunk proof. Metadata marks it `set_a_probe_candidate=false` and `set_b_control_candidate=true`. |
| `run_radius_graph_component_signature_3d_prepared_session` | Step-4 ready by local audit | Reports fixed-radius self-query to grouped-stream component-signature trunk and `grouped_stream_component_size_signature_3d`. Prior focused POD result was parity/not material. |
| `run_point_location_topology_stream_prepared_session` | Step-4 ready by local audit | Reports point-location topology stream trunk and continuation contract. Prior focused POD result was not material. |
| `run_segment_intersection_topology_stream_prepared_session` | Step-4 ready by local audit | Reports segment-intersection topology stream trunk and continuation contract. This is a core-helper assertion, not POD evidence. |
| `run_grouped_vector_sum_2d_prepared_session` | Step-4 ready by local audit | M36 generic grouped-reduction helper reports productized runner use, explicit Numba partner, internal output-column reuse, no hot-path host materialization, row contract, and `generic_grouped_vector_sum_f64x2`. This is local contract readiness, not performance evidence. |
| `run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session` | Step-4 ready by local audit | Reports aggregate-tree fused weighted vector-sum trunk and continuation contract. M29 same-contract boundary still applies. |
| `run_ray_triangle_weighted_summary_device_output_stream_prepared_session` | Step-4 ready by local audit | Reports ray-triangle weighted-summary device-output trunk and continuation contract; focused Triangle packet remains scoped. |

## Read

The current local audit surface has eight runner-callable continuation
families, one blocked Set-A seed, and three explicitly blocked Set-B controls.

`Step-4 ready by local audit` still means structural audit readiness. It does
not mean measured material speedup, release readiness, or all-app authorization.

## Validation

M36 local validation is recorded by the prepared-session runner test and the
surface-ledger gate:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_prepared_session_surface_ledger_gate_test \
  tests.v3_release_wording_gate_test
```

## Non-Authorization

This ledger authorizes no V3 release, no all-app POD spend, no public speedup
claims, no broad V3-over-V2.x claims, no true-zero-copy wording, no automatic
partner selection, no V4 work, no C ABI work, and no embedding work.
