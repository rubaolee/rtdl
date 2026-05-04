# Goal1066 Rejected RTX Local Remediation Manifest

Date: 2026-04-28

Valid: `true`

Goal1066 is a local remediation manifest for rejected RTX rows. It does not run cloud, change public wording, authorize release, or authorize public RTX speedup claims.

## Summary

- rejected rows: `5`
- remediation classes: `{'code_path_profile': 2, 'rt_mapping_profile': 1, 'chunking_and_candidate_discovery': 2}`
- missing remediation: `[]`

## Rows

| App | Path | Class | Pod policy | Local probe | Acceptance before pod |
| --- | --- | --- | --- | --- | --- |
| `database_analytics` | `prepared_db_session_sales_risk` | `code_path_profile` | `no_pod_until_code_or_scale_changes` | `PYTHONPATH=src:. python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies 20000 --iterations 3 --output-mode compact_summary --strict --output-json /tmp/goal1066_db_sales_optix.json` | phase breakdown identifies whether OptiX query, prepare, or Python/native transfer dominates; a concrete code or scale change is recorded before any cloud rerun |
| `database_analytics` | `prepared_db_session_regional_dashboard` | `code_path_profile` | `no_pod_until_code_or_scale_changes` | `PYTHONPATH=src:. python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario regional_dashboard --copies 20000 --iterations 3 --output-mode compact_summary --strict --output-json /tmp/goal1066_db_dashboard_optix.json` | grouped aggregation and compact-summary copyback costs are separated; a concrete code or scale change is recorded before any cloud rerun |
| `graph_analytics` | `graph_visibility_edges_gate` | `rt_mapping_profile` | `no_pod_until_code_or_scale_changes` | `PYTHONPATH=src:. python3 scripts/goal889_graph_visibility_optix_gate.py --copies 2000 --output-mode summary --validation-mode analytic_summary --chunk-copies 0 --strict --output-json /tmp/goal1066_graph_visibility_dry_probe.json` | RT traversal timing is separated from graph bookkeeping and validation; a local decision exists on whether to optimize the RT mapping or change the benchmark scale |
| `polygon_pair_overlap_area_rows` | `polygon_pair_overlap_optix_native_assisted_phase_gate` | `chunking_and_candidate_discovery` | `no_pod_until_code_or_scale_changes` | `PYTHONPATH=src:. python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app pair_overlap --mode dry-run --copies 2000 --output-mode summary --validation-mode analytic_summary --chunk-copies 100 --output-json /tmp/goal1066_pair_overlap_dry_probe.json` | candidate discovery row volume and chunking costs are bounded before cloud; PostGIS/Embree baseline mismatch is addressed before any public wording review |
| `polygon_set_jaccard` | `polygon_set_jaccard_optix_native_assisted_phase_gate` | `chunking_and_candidate_discovery` | `no_pod_until_code_or_scale_changes` | `PYTHONPATH=src:. python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode dry-run --copies 2000 --output-mode summary --validation-mode analytic_summary --chunk-copies 20 --output-json /tmp/goal1066_jaccard_dry_probe.json` | Jaccard candidate discovery avoids known large-chunk diagnostic failures; exact set-area/Jaccard CPU handoff is clearly outside the RT claim |

## Boundary

Goal1066 is a local remediation manifest for rejected RTX rows. It does not run cloud, change public wording, authorize release, or authorize public RTX speedup claims.
