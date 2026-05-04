# RTDL v1.0 Release Candidate Support Matrix

Status: draft release candidate for `v1.0`; not released.

This matrix summarizes the intended `v1.0` public support boundary. For the
living current-main app inventory, use `docs/v1_0_app_acceleration_inventory.md`.
For exact reviewed RTX wording rows, use `docs/v1_0_rtx_app_status.md`.

## Public RTX Wording Surface

Reviewed bounded NVIDIA RTX public wording rows: `12`.

| App / sub-path | Public wording status | Public claim allowed for v1.0 RC | Boundary |
| --- | --- | --- | --- |
| `service_coverage_gaps / prepared_gap_summary` | reviewed | yes | prepared fixed-radius gap-summary query/native sub-path only |
| `event_hotspot_screening / prepared_count_summary` | reviewed | yes | prepared fixed-radius count-summary query phase only |
| `facility_knn_assignment / coverage_threshold_prepared_recentered` | reviewed | yes | prepared facility coverage-threshold query sub-path only |
| `road_hazard_screening / prepared_native_compact_summary_40k` | reviewed | yes | prepared compact-summary traversal/count sub-path at 40k copies only |
| `segment_polygon_hitcount / segment_polygon_hitcount_native_experimental` | reviewed | yes | prepared native segment/polygon hit-count traversal only |
| `segment_polygon_anyhit_rows / segment_polygon_anyhit_rows_prepared_bounded_gate` | reviewed | yes | prepared bounded native pair-row traversal only |
| `hausdorff_distance / directed_threshold_prepared` | reviewed | yes | prepared Hausdorff <= radius threshold-decision traversal sub-path only |
| `ann_candidate_search / candidate_threshold_prepared` | reviewed | yes | prepared ANN candidate-coverage decision sub-path only |
| `outlier_detection / prepared_fixed_radius_density_summary` | reviewed | yes | prepared fixed-radius scalar threshold-count sub-path only |
| `dbscan_clustering / prepared_fixed_radius_core_flags` | reviewed | yes | prepared fixed-radius scalar core-count sub-path only |
| `robot_collision_screening / prepared_pose_flags` | reviewed | yes | prepared ray/triangle any-hit pose-count query sub-path only; ratio wording is normalized per-pose |
| `barnes_hut_force_app / node_coverage_prepared_rich` | reviewed | yes | prepared Barnes-Hut node-coverage query sub-path only, not force reduction |

## Blocked, Not-Reviewed, Or Non-NVIDIA Rows

| App row | v1.0 RC status | What would unblock public speedup wording |
| --- | --- | --- |
| `database_analytics` | not reviewed for current public speedup wording | Same-contract evidence with clear query contract, same result schema, and reviewed OptiX-vs-baseline speedup above the public threshold. |
| `graph_analytics` | blocked | Same-contract evidence where the reviewed OptiX traversal path is faster than the Embree baseline for the exact bounded graph/candidate traversal being described. |
| `polygon_pair_overlap_area_rows` | blocked | Same-contract evidence where the reviewed OptiX row path is faster than Embree and excludes unrelated polygon-area continuation work. |
| `polygon_set_jaccard` | not reviewed for current public speedup wording | Same-scale correctness and same-contract performance evidence for the exact Jaccard candidate/hitcount sub-path, plus external review. |
| `apple_rt_demo` | non-NVIDIA target | Apple RT support wording only; no NVIDIA RTX speedup claim needed. |
| `hiprt_ray_triangle_hitcount` | non-NVIDIA target | HIPRT support wording only; no NVIDIA RTX speedup claim needed. |

## Backend Notes

- OptiX/RTX wording is bounded to reviewed sub-path evidence, not whole-app
  speedup.
- Embree remains the CPU native baseline for many same-contract comparisons.
- Vulkan, HIPRT, and Apple RT have selected proof surfaces in current docs, but
  no additional v1.0 pod or promotion work is required unless the release scope
  changes.
- A successful backend run is evidence that the backend path can execute; it is
  not automatically evidence for public speedup wording.

## v1.5 And v2.0 Handoff

v1.0 accepts app-specific native continuations when they are required to prove
the app-shaped DSL boundary. The v1.5 target is to replace those continuations
with reviewed generic primitives:

- `ANY_HIT`;
- `COUNT_HITS`;
- `REDUCE_FLOAT(MIN|MAX|SUM)`;
- `REDUCE_INT(COUNT|SUM)`;
- experimental `COLLECT_K_BOUNDED`.

v2.0 is the later end-to-end performance architecture, not a claim made by this
v1.0 release candidate.
