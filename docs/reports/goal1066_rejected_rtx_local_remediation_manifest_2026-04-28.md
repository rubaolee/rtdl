# Goal1066 Rejected RTX Local Remediation Manifest

Date: 2026-04-28

Valid: `true`

Goal1066 is a local remediation manifest for rejected RTX rows. It does not run cloud, change public wording, authorize release, or authorize public RTX speedup claims.

## Summary

- rejected rows: `8`
- remediation classes: `{'code_path_profile': 3, 'rt_mapping_profile': 1, 'chunking_and_candidate_discovery': 2, 'scale_contract_repair': 2}`
- missing remediation: `[]`

## Rows

| App | Path | Class | Pod policy | Local probe | Acceptance before pod |
| --- | --- | --- | --- | --- | --- |
| `database_analytics` | `prepared_db_session_sales_risk` | `code_path_profile` | `no_pod_until_code_or_scale_changes` | `PYTHONPATH=src:. python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies 20000 --iterations 3 --output-mode compact_summary --strict --output-json /tmp/goal1066_db_sales_optix.json` | phase breakdown identifies whether OptiX query, prepare, or Python/native transfer dominates; a concrete code or scale change is recorded before any cloud rerun |
| `database_analytics` | `prepared_db_session_regional_dashboard` | `code_path_profile` | `no_pod_until_code_or_scale_changes` | `PYTHONPATH=src:. python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario regional_dashboard --copies 20000 --iterations 3 --output-mode compact_summary --strict --output-json /tmp/goal1066_db_dashboard_optix.json` | grouped aggregation and compact-summary copyback costs are separated; a concrete code or scale change is recorded before any cloud rerun |
| `graph_analytics` | `graph_visibility_edges_gate` | `rt_mapping_profile` | `no_pod_until_code_or_scale_changes` | `PYTHONPATH=src:. python3 scripts/goal889_graph_visibility_optix_gate.py --copies 2000 --output-mode summary --validation-mode analytic_summary --chunk-copies 0 --strict --output-json /tmp/goal1066_graph_visibility_dry_probe.json` | RT traversal timing is separated from graph bookkeeping and validation; a local decision exists on whether to optimize the RT mapping or change the benchmark scale |
| `road_hazard_screening` | `road_hazard_native_summary_gate` | `code_path_profile` | `no_pod_until_code_or_scale_changes` | `PYTHONPATH=src:. python3 scripts/goal933_prepared_segment_polygon_optix_profiler.py --scenario road_hazard_prepared_summary --copies 2000 --iterations 3 --mode dry-run --output-json /tmp/goal1066_road_hazard_dry_probe.json` | same-semantics Embree advantage is explained or a native OptiX optimization target is identified; no cloud rerun until the prepared segment/polygon summary path changes or a new scale contract exists |
| `polygon_pair_overlap_area_rows` | `polygon_pair_overlap_optix_native_assisted_phase_gate` | `chunking_and_candidate_discovery` | `no_pod_until_code_or_scale_changes` | `PYTHONPATH=src:. python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app pair_overlap --mode dry-run --copies 2000 --output-mode summary --validation-mode analytic_summary --chunk-copies 100 --output-json /tmp/goal1066_pair_overlap_dry_probe.json` | candidate discovery row volume and chunking costs are bounded before cloud; PostGIS/Embree baseline mismatch is addressed before any public wording review |
| `polygon_set_jaccard` | `polygon_set_jaccard_optix_native_assisted_phase_gate` | `chunking_and_candidate_discovery` | `no_pod_until_code_or_scale_changes` | `PYTHONPATH=src:. python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode dry-run --copies 2000 --output-mode summary --validation-mode analytic_summary --chunk-copies 20 --output-json /tmp/goal1066_jaccard_dry_probe.json` | Jaccard candidate discovery avoids known large-chunk diagnostic failures; exact set-area/Jaccard CPU handoff is clearly outside the RT claim |
| `hausdorff_distance` | `directed_threshold_prepared` | `scale_contract_repair` | `no_pod_until_scale_contract_changes` | `PYTHONPATH=src:. python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario hausdorff_threshold --mode dry-run --copies 20000 --iterations 1 --radius 0.4 --output-json /tmp/goal1066_hausdorff_dry_probe.json` | CPU same-semantics baseline is no longer microsecond-trivial or is explicitly excluded as a claim baseline; the threshold-decision scale remains semantically meaningful and dry-run validated |
| `barnes_hut_force_app` | `node_coverage_prepared` | `scale_contract_repair` | `no_pod_until_scale_contract_changes` | `PYTHONPATH=src:. python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode dry-run --body-count 200000 --iterations 1 --radius 10.0 --output-json /tmp/goal1066_barnes_hut_dry_probe.json` | CPU same-semantics baseline is no longer trivial or the benchmark target is reframed away from a speedup claim; node-coverage remains bounded to candidate discovery, not force-vector reduction |

## Boundary

Goal1066 is a local remediation manifest for rejected RTX rows. It does not run cloud, change public wording, authorize release, or authorize public RTX speedup claims.
