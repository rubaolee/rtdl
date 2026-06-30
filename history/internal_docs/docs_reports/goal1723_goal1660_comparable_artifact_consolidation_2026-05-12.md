# Goal1723 Goal1660 Comparable Artifact Consolidation

## Verdict

`accept-with-boundary`

The 16 real v1.0/v1.6.11 comparable rows have artifact pairs present. Three timing artifacts carried evidence-boundary notes, and Goal1726 adds companion evidence for all three. This remains a consolidation of pod output only; it does not authorize release, tagging, or public speedup wording.

## Summary

- Planned comparable rows: `16`
- Artifact pairs present: `16`
- Rows with clean parity or companion evidence: `16`
- Timing-artifact boundary rows: `3`
- Companion resolutions: `3`
- Unresolved boundaries: `0`
- Public claim authorized: `False`

## Rows

| App | Engine | Current status | v1.0 status | Evidence ready | Semantic digest equal | Timing boundary | Companion resolution |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `database_analytics` | `embree` | `ok` | `ok` | `True` | `True` | `none` | `none` |
| `database_analytics` | `optix` | `ok` | `ok` | `True` | `True` | `none` | `none` |
| `graph_analytics` | `optix` | `pass` | `pass` | `True` | `None` | `none` | `none` |
| `service_coverage_gaps` | `optix` | `None` | `None` | `True` | `True` | `none` | `none` |
| `event_hotspot_screening` | `optix` | `None` | `None` | `True` | `True` | `none` | `none` |
| `facility_knn_assignment` | `optix` | `None` | `None` | `True` | `True` | `skip_validation_true_in_profiler_payload` | `validation_companion_matches_oracle` |
| `road_hazard_screening` | `optix` | `pass` | `pass` | `True` | `True` | `none` | `none` |
| `segment_polygon_hitcount` | `optix` | `pass` | `pass` | `True` | `True` | `none` | `none` |
| `segment_polygon_anyhit_rows` | `optix` | `pass` | `pass` | `True` | `True` | `none` | `none` |
| `polygon_pair_overlap_area_rows` | `optix` | `pass` | `pass` | `True` | `True` | `none` | `none` |
| `polygon_set_jaccard` | `optix` | `diagnostic_chunk_config` | `diagnostic_chunk_config` | `True` | `True` | `diagnostic_chunk_config_not_public_safe` | `public_safe_chunk_companion_passes_parity` |
| `hausdorff_distance` | `optix` | `None` | `None` | `True` | `True` | `none` | `none` |
| `ann_candidate_search` | `optix` | `None` | `None` | `True` | `True` | `none` | `none` |
| `outlier_detection` | `optix` | `None` | `None` | `True` | `None` | `none` | `none` |
| `robot_collision_screening` | `optix` | `None` | `None` | `True` | `True` | `validated_false_in_profiler_payload` | `pose_flags_validation_companion_matches_oracle` |
| `barnes_hut_force_app` | `optix` | `None` | `None` | `True` | `True` | `none` | `none` |

## Boundary

Timing fields are inventoried for later human/statistical review, but this report deliberately does not compute or publish speedups. Semantic digests intentionally exclude timing and run metadata. Companion evidence resolves validation/chunk-safety boundaries for evidence hygiene, but release and public wording remain blocked pending final release review.
