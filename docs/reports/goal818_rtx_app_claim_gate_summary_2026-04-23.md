# Goal 818: RTX App Claim-Gate Summary

Date: 2026-04-23

Status: complete

## Purpose

This report summarizes the local-first app claim-gate work after Goals 813-817.
It is meant to answer one practical release question:

> If a public RTDL app exposes or might later expose NVIDIA OptiX, can a user or
> benchmark script accidentally treat a non-RT-core path as an RT-core claim?

Current answer: no known public app should silently enter that state. Apps are
either claim-ready only for bounded prepared sub-paths, partial with explicit
scope, or guarded/excluded with fail-fast `--require-rt-core` behavior.

## Status Table

| App | Current NVIDIA RT-core status | Guard / claim boundary |
| --- | --- | --- |
| `database_analytics` | `rt_core_partial_ready` | `--require-rt-core` allowed only for `--backend optix --output-mode compact_summary`; broad DB speedup remains disallowed. |
| `graph_analytics` | `needs_rt_core_redesign` | `--require-rt-core` rejects the current host-indexed OptiX CSR fallback. |
| `service_coverage_gaps` | `rt_core_partial_ready` | `--require-rt-core` allowed only for `--backend optix --optix-summary-mode gap_summary_prepared`; needs phase-clean RTX evidence before any claim. |
| `event_hotspot_screening` | `rt_core_partial_ready` | `--require-rt-core` allowed only for `--backend optix --optix-summary-mode count_summary_prepared`; needs phase-clean RTX evidence before any claim. |
| `facility_knn_assignment` | `needs_optix_app_surface` | No OptiX app surface; KNN ranking cannot be replaced by fixed-radius threshold counts. |
| `road_hazard_screening` | `needs_rt_core_redesign` | `--require-rt-core` rejects even native mode until strict segment/polygon RTX validation passes. |
| `segment_polygon_hitcount` | `needs_rt_core_redesign` | `--require-rt-core` rejects even native hit-count mode until strict Goal807 RTX validation passes. |
| `segment_polygon_anyhit_rows` | `needs_rt_core_redesign` | `--require-rt-core` rejects compact native mode until strict Goal807 RTX validation passes; pair-row native emitter does not exist. |
| `polygon_pair_overlap_area_rows` | `needs_optix_app_surface` | `--require-rt-core` rejects because there is no OptiX app surface today. |
| `polygon_set_jaccard` | `needs_optix_app_surface` | `--require-rt-core` rejects because there is no OptiX app surface today. |
| `hausdorff_distance` | `needs_rt_core_redesign` | `--require-rt-core` rejects CUDA-through-OptiX KNN rows. |
| `ann_candidate_search` | `needs_rt_core_redesign` | `--require-rt-core` rejects CUDA-through-OptiX KNN rows. |
| `outlier_detection` | `rt_core_ready` | Only the prepared scalar threshold-count sub-path may enter RTX claim review. |
| `dbscan_clustering` | `rt_core_ready` | Only the prepared core-threshold summary sub-path may enter RTX claim review. |
| `robot_collision_screening` | `rt_core_ready` | Prepared ray/triangle any-hit scalar pose-count is the current flagship claim path. |
| `barnes_hut_force_app` | `needs_rt_core_redesign` | `--require-rt-core` rejects CUDA-through-OptiX radius candidate generation. |
| `apple_rt_demo` | `not_nvidia_rt_core_target` | Apple-specific; excluded from NVIDIA cloud batches. |
| `hiprt_ray_triangle_hitcount` | `not_nvidia_rt_core_target` | HIPRT-specific; excluded from NVIDIA OptiX batches. |

## New Gates Added

| Goal | Scope | Main result |
| --- | --- | --- |
| Goal813 | Facility KNN | Prevents KNN ranking from being reclassified as fixed-radius threshold traversal. |
| Goal814 | Graph analytics | Adds `--require-rt-core` rejection for host-indexed OptiX graph fallback. |
| Goal815 | DB analytics | Allows `--require-rt-core` only for bounded OptiX compact-summary DB path. |
| Goal816 | Polygon overlap/Jaccard | Adds `--require-rt-core` rejection for apps with no OptiX surface. |
| Goal817 | Hausdorff/ANN/Barnes-Hut | Adds `--require-rt-core` rejection for CUDA-through-OptiX compute paths. |
| Goal819 | Service coverage / event hotspot | Adds `--require-rt-core` enforcement for prepared OptiX summary modes only. |
| Goal820 | Segment/polygon apps | Adds `--require-rt-core` rejection until strict native RTX validation passes. |

## Verification

Aggregated local gate suite:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal813_facility_knn_rt_core_boundary_test \
  tests.goal814_graph_optix_rt_core_honesty_gate_test \
  tests.goal815_db_rt_core_claim_gate_test \
  tests.goal816_polygon_overlap_rt_core_boundary_test \
  tests.goal817_cuda_through_optix_claim_gate_test \
  tests.goal818_rtx_claim_gate_summary_test \
  tests.goal819_spatial_prepared_summary_rt_core_gate_test \
  tests.goal820_segment_polygon_rt_core_gate_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal803_rt_core_app_maturity_contract_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal761_rtx_cloud_run_all_test
```

Current result after Goals813-820: `66 tests OK`.

## Cloud Policy

Do not restart a paid cloud pod per app. The current cloud-ready set remains a
batched validation problem:

- active claim-review paths: outlier prepared summary, DBSCAN prepared summary,
  robot prepared pose-count;
- partial/deferred readiness gates: DB compact summary, service/event prepared
  summaries, segment/polygon strict native gate;
- excluded/gated apps must not be benchmarked as RT-core claims.

## Release Boundary

This report is a claim-safety summary. It does not promote any app beyond the
machine-readable statuses in `rtdsl.rt_core_app_maturity_matrix()` and
`rtdsl.optix_app_benchmark_readiness_matrix()`.
