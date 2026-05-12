# Goal1750 Same-Contract Performance Summary

## Verdict

`same_contract_perf_summary_ready_without_public_claim`

This summary compares available v1.0 customized-engine artifacts against current generic-engine artifacts. OptiX has broad same-contract primary ratios; Embree has one historical same-contract database row plus recovered Goal1746 app-level rows that remain diagnostic or schema-mismatched. No public speedup or release claim is authorized.

## OptiX

- Artifact-pair rows: `17`
- `same_contract_primary_ratio`: `17`

| App | Classification | Phase | v1.0 sec | Current sec | v1.0/current |
| --- | --- | --- | ---: | ---: | ---: |
| `database_analytics` | `same_contract_primary_ratio` | `prepared_session_warm_query_median` | 0.0746274 | 0.0741169 | 1.00689 |
| `service_coverage_gaps` | `same_contract_primary_ratio` | `optix_query` | 0.178277 | 0.15212 | 1.17196 |
| `event_hotspot_screening` | `same_contract_primary_ratio` | `optix_query` | 0.183431 | 0.182763 | 1.00365 |
| `facility_knn_assignment` | `same_contract_primary_ratio` | `query_median` | 0.000823678 | 0.000872586 | 0.943951 |
| `road_hazard_screening` | `same_contract_primary_ratio` | `query_median` | 0.102807 | 0.103605 | 0.992293 |
| `segment_polygon_hitcount` | `same_contract_primary_ratio` | `query_median` | 0.00242895 | 0.00243017 | 0.999497 |
| `segment_polygon_anyhit_rows` | `same_contract_primary_ratio` | `query_median` | 0.00409926 | 0.0039009 | 1.05085 |
| `polygon_pair_overlap_area_rows` | `same_contract_primary_ratio` | `candidate_discovery` | 4.0347 | 2.85735 | 1.41204 |
| `polygon_set_jaccard` | `same_contract_primary_ratio` | `candidate_discovery` | 2.37142 | 2.46872 | 0.960588 |
| `hausdorff_distance` | `same_contract_primary_ratio` | `query_median` | 0.00161574 | 0.00170234 | 0.949129 |
| `ann_candidate_search` | `same_contract_primary_ratio` | `query_median` | 0.000525368 | 0.000530187 | 0.990911 |
| `outlier_detection` | `same_contract_primary_ratio` | `warm_query_median` | 0.00167848 | 0.0016726 | 1.00352 |
| `robot_collision_screening` | `same_contract_primary_ratio` | `prepared_pose_flags_warm_query_median` | 0.000356678 | 0.000352647 | 1.01143 |
| `barnes_hut_force_app` | `same_contract_primary_ratio` | `query_median` | 0.00176794 | 0.0017695 | 0.999118 |
| `graph_visibility_edges` | `same_contract_primary_ratio` | `graph_section_wall` | 0.959978 | 0.635912 | 1.50961 |
| `graph_bfs` | `same_contract_primary_ratio` | `graph_section_wall` | 6.23224 | 0.71636 | 8.69987 |
| `graph_triangle_count` | `same_contract_primary_ratio` | `graph_section_wall` | 0.88762 | 0.971441 | 0.913715 |

## Embree

- Same-contract artifact-pair rows: `1`
- Goal1746 recovered app-level rows: `14`
- Goal1748 `missing_current_artifact`: `3`
- Goal1748 `phase_mapped_diagnostic`: `4`
- Goal1748 `timing_schema_mismatch`: `7`

| App | Classification | Phase | v1.0 sec | Current sec | v1.0/current |
| --- | --- | --- | ---: | ---: | ---: |
| `database_analytics` | `same_contract_primary_ratio` | `prepared_session_warm_query_median` | 0.0833325 | 0.0824235 | 1.01103 |

Goal1748 recovered Embree rows remain bounded as follows:

| Classification | Count | Meaning |
| --- | ---: | --- |
| `phase_mapped_diagnostic` | 4 | Numeric mappings exist, but they are diagnostic and not public same-contract claims. |
| `timing_schema_mismatch` | 7 | Artifacts exist, but timing schemas do not yet support a same-contract ratio. |
| `missing_current_artifact` | 3 | v1.0 split graph artifacts exist, but no same-name current Embree artifact exists. |

## Boundary

Use this as internal engineering evidence only. It answers whether the generic-engine rewrite caused obvious same-contract regressions where comparable timing exists; it does not authorize public speedup language, v1.8 release, or a broad statement over rows classified as diagnostic or schema-mismatched.
