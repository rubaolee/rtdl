# Goal822 RTX Cloud Manifest Claim Boundary Audit

Date: 2026-04-23

## Verdict

ACCEPT. The current cloud benchmark manifest is consistent with the app-level
NVIDIA RT-core claim gates added through Goals 813-821.

## Active Cloud Entries

The active manifest entries are limited to apps whose machine-readable maturity
status is `rt_core_ready` or `rt_core_partial_ready`:

| App | Active path | Status | Boundary |
| --- | --- | --- | --- |
| `database_analytics` | prepared DB session, sales risk | `rt_core_partial_ready` | compact-summary/interface split only |
| `database_analytics` | prepared DB session, regional dashboard | `rt_core_partial_ready` | compact-summary/interface split only |
| `outlier_detection` | prepared fixed-radius density summary | `rt_core_ready` | threshold-count summary only |
| `dbscan_clustering` | prepared fixed-radius core flags | `rt_core_ready` | core-flag summary only |
| `robot_collision_screening` | prepared pose flags/count | `rt_core_ready` | prepared ray/triangle any-hit compact summary only |

These active entries are not broad app-speedup claims. Each command records a
bounded `claim_scope`, a `non_claim`, and required RTX hardware preconditions.

## Deferred Entries

`service_coverage_gaps` and `event_hotspot_screening` are intentionally
deferred. They have accepted app-level `--require-rt-core` prepared summary
modes, but their benchmark readiness remains `needs_phase_contract`. They
should only be promoted after Goal811 phase-profiler evidence is collected on
RTX hardware and reviewed.

`segment_polygon_hitcount` is also deferred behind Goal807 strict native-mode
validation because the current default app path remains host-indexed.

## Excluded Apps

The manifest excludes the current non-claim app families from active cloud
timing:

- `graph_analytics`
- `facility_knn_assignment`
- `road_hazard_screening`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`
- `hausdorff_distance`
- `ann_candidate_search`
- `barnes_hut_force_app`
- `apple_rt_demo`
- `hiprt_ray_triangle_hitcount`

This preserves the release red line: do not spend cloud budget timing apps as
RT-core claims when the current app path is host-indexed, CUDA-through-OptiX,
not OptiX-exposed, or not an NVIDIA target.

## Verification

Added `/Users/rl2025/rtdl_python_only/tests/goal822_rtx_cloud_manifest_claim_boundary_test.py`.

The test verifies:

- active cloud entries are only `rt_core_ready` or `rt_core_partial_ready`;
- active entries do not use `cuda_through_optix`, `host_indexed_fallback`, or
  `not_optix_exposed` performance classes;
- known non-claim app families are excluded from active entries;
- service/hotspot prepared summary apps remain deferred until Goal811 phase
  evidence exists.

This goal is local pre-cloud work. It does not authorize starting a paid cloud
pod and does not authorize RTX speedup claims.
