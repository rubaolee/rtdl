# Goal4344: Embree Same-Contract Scale Probe

Date: 2026-06-11

Status: internal Embree scale evidence; not comparison or release authorization.

## Verdict

Goal4344 moves the five previously missing Embree scale rows out of the `needs_same_contract_scale_pair` bucket. Three are clean query-ratio candidates against the current OptiX scale artifacts; Robot Collision and RayDB-style are scale-ready but boundary-limited because their current OptiX rows use stronger resident/device output paths.

## Embree Rows

| App | Artifact | Comparison Class | Metric | Value | Correctness | Boundary |
| --- | --- | --- | --- | ---: | --- | --- |
| hausdorff_xhd | `hausdorff_embree_threshold_1024` | `same_contract_query_ratio_candidate` | `max_directed_query_fixed_radius_threshold_reached_count_sec` | 0.009892253 sec | `{'matches_oracle': True, 'oracle_decision_matches': True}` | Same prepared fixed-radius threshold decision contract as the current OptiX row. This is still smoke/internal timing evidence. |
| robot_collision | `robot_embree_prepared_buffers_1024_128_4_50000` | `same_scene_query_scale_output_residency_boundary` | `tail_median_traversal_sec` | 0.000995346 sec | `{'probe_reference_validated': False, 'all_run_signatures_identical': True, 'no_probe_reference_matches_current_optix_scale_policy': True}` | Same scene/query scale as the current OptiX row, but Embree returns host compact flags while the current OptiX row uses an OptiX-only device-count path. Traversal phase is useful internally; total/output ratios are not clean backend ratios. |
| contact_manifold | `contact_embree_grid64_witness128` | `same_contract_query_ratio_candidate` | `native_collect_elapsed_sec` | 0.000260988 sec | `{'matches_cpu_reference': True, 'complete_candidate_coverage': True, 'overflowed': False}` | Same bounded collect-k contract, grid size, witness capacity, and repeat count as OptiX. |
| raydb_style | `raydb_embree_count_generated_262144_1024` | `same_scale_prepared_residency_boundary` | `native_grouped_reduction_traversal_sec` | 0.012958745 sec | `{'matches_cpu_reference': True, 'embree_same_contract_baseline': True}` | Same generated row/group scale and grouped-count result contract as the current OptiX row, but the OptiX scale row is a prepared resident v2.5 primitive-first path while this Embree row is a non-resident native grouped-reduction run. Clean end-to-end ratios are withheld. |
| triangle_counting | `triangle_embree_rtgraph2a1_2048` | `same_contract_query_ratio_candidate` | `query_median_ms` | 11.54467 ms | `{'triangle_count_matches_oracle': True, 'generic_rt_weighted_triangle_count': 4096, 'oracle_triangle_count': 4096}` | Same RT-Graph 2A1 fixture, copy count, detail mode, repeat, and warmup as OptiX. |

## Summary

- Embree scale artifacts: 5
- Clean query-ratio candidates: 3
- Boundary-limited scale artifacts: 2
- All process statuses zero: True

## Boundary

Goal4344 records fresh Embree CPU scale artifacts for the five rows that Goal4343 previously marked as needing same-contract scale evidence. It does not authorize release action, public speedup wording, whole-app acceleration wording, Intel GPU performance wording, paper reproduction wording, true-zero-copy wording, automatic partner selection, or app-specific native-engine logic.

Validation status: `accept`.
