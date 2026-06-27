# Goal1193 Public Wording Evidence Batch Intake

Date: 2026-04-30

Valid schema: `True`
Input dir: `docs/reports/goal1194_live_pod_2026-04-30/final_recovery2/docs/reports/goal1192_public_wording_evidence_batch`
Timing floor: `0.1` seconds

## Pair Readiness

| App | Schema valid | Timing floor met | Embree phase sec | OptiX phase sec | Raw ratio | Public wording review ready |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `database_analytics` | `True` | `True` | `0.11934712203219533` | `0.15072045754641294` | `0.791844` | `True` |
| `graph_analytics` | `True` | `True` | `1.0002804789692163` | `2.000505495816469` | `0.500014` | `True` |
| `road_hazard_screening` | `True` | `True` | `0.41562127228826284` | `0.10353890899568796` | `4.01416` | `True` |
| `polygon_pair_overlap_area_rows` | `True` | `True` | `2.89659671112895` | `3.4523619720712304` | `0.839019` | `True` |
| `polygon_set_jaccard` | `True` | `True` | `0.8894528830423951` | `1.6208405895158648` | `0.54876` | `True` |
| `hausdorff_distance` | `True` | `True` | `1.6802135026082397` | `0.12238904647529125` | `13.7285` | `True` |

## Artifact Schema

| Artifact | Exists | Schema valid | Phase path | Phase sec | Timing floor | Problems |
| --- | --- | --- | --- | ---: | --- | --- |
| `database_compact_summary_embree.json` | `True` | `True` | `results.0.prepared_session_warm_query_sec.median_sec` | `0.11934712203219533` | `True` | none |
| `database_compact_summary_optix.json` | `True` | `True` | `results.0.prepared_session_warm_query_sec.median_sec` | `0.15072045754641294` | `True` | none |
| `graph_visibility_edges_embree.json` | `True` | `True` | `graph_phase_totals_sec.query_visibility_pair_rows_sec` | `1.0002804789692163` | `True` | none |
| `graph_visibility_edges_optix.json` | `True` | `True` | `records_by_label.optix_visibility_anyhit.sec` | `2.000505495816469` | `True` | none |
| `road_hazard_native_summary_embree.json` | `True` | `True` | `run_phases.query_and_materialize_sec` | `0.41562127228826284` | `True` | none |
| `road_hazard_native_summary_optix.json` | `True` | `True` | `timings_sec.optix_query_sec.median_sec` | `0.10353890899568796` | `True` | none |
| `polygon_pair_candidate_discovery_embree.json` | `True` | `True` | `run_phases.rt_candidate_discovery_sec` | `2.89659671112895` | `True` | none |
| `polygon_pair_candidate_discovery_optix.json` | `True` | `True` | `phases.optix_candidate_discovery_sec` | `3.4523619720712304` | `True` | none |
| `polygon_jaccard_safe_chunk_embree.json` | `True` | `True` | `run_phases.rt_candidate_discovery_sec` | `0.8894528830423951` | `True` | none |
| `polygon_jaccard_safe_chunk_optix.json` | `True` | `True` | `phases.optix_candidate_discovery_sec` | `1.6208405895158648` | `True` | none |
| `hausdorff_threshold_prepared_embree.json` | `True` | `True` | `run_phases.native_directed_summary_sec` | `1.6802135026082397` | `True` | none |
| `hausdorff_threshold_prepared_optix.json` | `True` | `True` | `scenario.timings_sec.optix_query_sec.median_sec` | `0.12238904647529125` | `True` | none |

## Archive

- archive exists: `False`
- archive readable: `False`
- sha256 file exists: `False`

## Boundary

This intake validates copied Goal1192 evidence artifacts only. It does not run cloud, does not authorize release, and does not authorize public RTX speedup wording by itself.

