# Goal1009 Public RTX Sub-Path Wording Review Packet

Date: 2026-04-26

Goal1009 packages candidate wording for external review. It does not edit public docs and does not authorize public speedup claims. The candidate wording is limited to prepared RTX A5000 query/native sub-paths with same-semantics non-OptiX baselines.

## Summary

- candidate wording rows: `7`
- blocked rows: `1`
- public speedup claims authorized here: `0`

## Candidate Rows

| App | Path | RTX phase (s) | Ratio | Fastest baseline | Source |
|---|---|---:|---:|---|---|
| `service_coverage_gaps` | `prepared_gap_summary` | 0.136545 | 1.61 | `embree_summary_path` | `goal1006` |
| `outlier_detection` | `prepared_fixed_radius_density_summary` | 0.122348 | 4.64 | `cpu_scalar_threshold_count_oracle` | `goal1008` |
| `dbscan_clustering` | `prepared_fixed_radius_core_flags` | 0.122921 | 6.62 | `cpu_scalar_threshold_count_oracle` | `goal1008` |
| `facility_knn_assignment` | `coverage_threshold_prepared` | 0.157368 | 22.81 | `cpu_oracle_same_semantics` | `goal1008` |
| `segment_polygon_hitcount` | `segment_polygon_hitcount_native_experimental` | 0.146860 | 1.71 | `embree_same_semantics` | `goal1008` |
| `segment_polygon_anyhit_rows` | `segment_polygon_anyhit_rows_prepared_bounded_gate` | 0.192639 | 3.03 | `postgis_when_available_for_same_pair_semantics` | `goal1008` |
| `ann_candidate_search` | `candidate_threshold_prepared` | 0.105215 | 4.86 | `cpu_oracle_same_semantics` | `goal1008` |

## Candidate Wording

### service_coverage_gaps / prepared_gap_summary

On the recorded RTX A5000 artifact set, the prepared RTDL `service_coverage_gaps / prepared_gap_summary` query/native sub-path had median RTX phase 0.136545 s and was 1.61x faster than the fastest same-semantics non-OptiX baseline for that measured sub-path. This is not a whole-app speedup claim, not a default-mode claim, and not a claim about Python-side postprocessing or unrelated app stages.

### outlier_detection / prepared_fixed_radius_density_summary

On the recorded RTX A5000 artifact set, the prepared RTDL `outlier_detection / prepared_fixed_radius_density_summary` query/native sub-path had median RTX phase 0.122348 s and was 4.64x faster than the fastest same-semantics non-OptiX baseline for that measured sub-path. This is not a whole-app speedup claim, not a default-mode claim, and not a claim about Python-side postprocessing or unrelated app stages.

### dbscan_clustering / prepared_fixed_radius_core_flags

On the recorded RTX A5000 artifact set, the prepared RTDL `dbscan_clustering / prepared_fixed_radius_core_flags` query/native sub-path had median RTX phase 0.122921 s and was 6.62x faster than the fastest same-semantics non-OptiX baseline for that measured sub-path. This is not a whole-app speedup claim, not a default-mode claim, and not a claim about Python-side postprocessing or unrelated app stages.

### facility_knn_assignment / coverage_threshold_prepared

On the recorded RTX A5000 artifact set, the prepared RTDL `facility_knn_assignment / coverage_threshold_prepared` query/native sub-path had median RTX phase 0.157368 s and was 22.81x faster than the fastest same-semantics non-OptiX baseline for that measured sub-path. This is not a whole-app speedup claim, not a default-mode claim, and not a claim about Python-side postprocessing or unrelated app stages.

### segment_polygon_hitcount / segment_polygon_hitcount_native_experimental

On the recorded RTX A5000 artifact set, the prepared RTDL `segment_polygon_hitcount / segment_polygon_hitcount_native_experimental` query/native sub-path had median RTX phase 0.146860 s and was 1.71x faster than the fastest same-semantics non-OptiX baseline for that measured sub-path. This is not a whole-app speedup claim, not a default-mode claim, and not a claim about Python-side postprocessing or unrelated app stages.

### segment_polygon_anyhit_rows / segment_polygon_anyhit_rows_prepared_bounded_gate

On the recorded RTX A5000 artifact set, the prepared RTDL `segment_polygon_anyhit_rows / segment_polygon_anyhit_rows_prepared_bounded_gate` query/native sub-path had median RTX phase 0.192639 s and was 3.03x faster than the fastest same-semantics non-OptiX baseline for that measured sub-path. This is not a whole-app speedup claim, not a default-mode claim, and not a claim about Python-side postprocessing or unrelated app stages.

### ann_candidate_search / candidate_threshold_prepared

On the recorded RTX A5000 artifact set, the prepared RTDL `ann_candidate_search / candidate_threshold_prepared` query/native sub-path had median RTX phase 0.105215 s and was 4.86x faster than the fastest same-semantics non-OptiX baseline for that measured sub-path. This is not a whole-app speedup claim, not a default-mode claim, and not a claim about Python-side postprocessing or unrelated app stages.

## Blocked Rows

- `robot_collision_screening / prepared_pose_flags` remains blocked: Still below the 100 ms public-review timing floor after larger RTX repeats. median RTX phase `0.014177` s.

## Reviewer Questions

- Is every candidate wording line accurately scoped to a prepared query/native sub-path?
- Does any line imply whole-app, default-mode, Python-postprocess, or broad RT-core acceleration?
- Are the blocked rows correctly excluded from public wording?

