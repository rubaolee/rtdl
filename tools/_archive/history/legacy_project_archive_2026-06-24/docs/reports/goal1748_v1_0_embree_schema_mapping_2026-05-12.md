# Goal1748 v1.0 Embree Schema Mapping

## Verdict

`embree_schema_mapping_ready_without_public_speedup_claim`

This report classifies recovered v1.0 Embree artifacts against current generic Embree artifacts. Ratios are diagnostic only unless a row has exact same-contract phase evidence and external review.

## Summary

- Rows classified: `14`
- Public claim authorized: `False`
- Release authorized: `False`
- `missing_current_artifact`: `3`
- `phase_mapped_diagnostic`: `4`
- `timing_schema_mismatch`: `7`

## Rows

| App | Classification | Diagnostic mappings |
| --- | --- | --- |
| `service_coverage_gaps` | `timing_schema_mismatch` | Timing fields exist, but no same-contract phase mapping is defined yet. |
| `event_hotspot_screening` | `timing_schema_mismatch` | Timing fields exist, but no same-contract phase mapping is defined yet. |
| `facility_knn_assignment` | `timing_schema_mismatch` | Timing fields exist, but no same-contract phase mapping is defined yet. |
| `road_hazard_screening` | `phase_mapped_diagnostic` | native_query_or_materialize=5.572x |
| `segment_polygon_hitcount` | `timing_schema_mismatch` | Timing fields exist, but no same-contract phase mapping is defined yet. |
| `segment_polygon_anyhit_rows` | `timing_schema_mismatch` | Timing fields exist, but no same-contract phase mapping is defined yet. |
| `graph_visibility_edges` | `missing_current_artifact` | Recovered v1.0 row exists, but there is no same-name current Embree artifact. |
| `graph_bfs` | `missing_current_artifact` | Recovered v1.0 row exists, but there is no same-name current Embree artifact. |
| `graph_triangle_count` | `missing_current_artifact` | Recovered v1.0 row exists, but there is no same-name current Embree artifact. |
| `hausdorff_distance` | `phase_mapped_diagnostic` | native_directed_or_query=177.903x |
| `ann_candidate_search` | `timing_schema_mismatch` | Timing fields exist, but no same-contract phase mapping is defined yet. |
| `barnes_hut_force_app` | `timing_schema_mismatch` | Timing fields exist, but no same-contract phase mapping is defined yet. |
| `polygon_pair_overlap_area_rows` | `phase_mapped_diagnostic` | rt_candidate_discovery=0.136x, native_exact_continuation=0.866x |
| `polygon_set_jaccard` | `phase_mapped_diagnostic` | rt_candidate_discovery=0.005x, native_exact_continuation=1.211x |

## ANN Long-Run Resolution

`ann_candidate_search` is present in the recovered v1.0 Embree set. The resolved command uses `--output-mode rerank_summary`; the rejected `quality_summary` path would perform roughly 7.2 billion Python exact-distance checks at Goal1660 scale and is not used as the baseline recovery surface.

## Boundary

This mapping does not authorize public speedup wording. Rows with diagnostic ratios still need exact same-contract confirmation before any performance claim, and rows classified as `summary_only`, `timing_schema_mismatch`, or `missing_current_artifact` cannot support a timing comparison.
