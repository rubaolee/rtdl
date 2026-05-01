# Goal974 Remaining Local Baselines

Date: 2026-04-26

## Scope

Goal974 collected all locally available baseline artifacts for the six rows that
remained baseline-pending after Goal973.

Rows covered:

- `graph_analytics / graph_visibility_edges_gate`
- `road_hazard_screening / road_hazard_native_summary_gate`
- `segment_polygon_hitcount / segment_polygon_hitcount_native_experimental`
- `segment_polygon_anyhit_rows / segment_polygon_anyhit_rows_prepared_bounded_gate`
- `polygon_pair_overlap_area_rows / polygon_pair_overlap_optix_native_assisted_phase_gate`
- `polygon_set_jaccard / polygon_set_jaccard_optix_native_assisted_phase_gate`

## Collected Artifacts

Goal974 wrote `13` local artifacts:

- road hazard: CPU reference and Embree same-semantics summaries
- segment/polygon hitcount: CPU reference and Embree same-semantics summaries
- segment/polygon bounded rows: CPU reference pair-row baseline
- polygon pair overlap: CPU reference and Embree native-assisted candidate-discovery baselines
- polygon set Jaccard: CPU reference and Embree native-assisted candidate-discovery baselines
- graph analytics: CPU visibility/BFS/triangle baselines plus Embree graph-ray baseline

Machine-readable run summary:

```text
docs/reports/goal974_remaining_local_baselines_2026-04-26.json
```

## Post-Collection Gate State

Goal836 now reports:

```text
valid_artifact_count: 37
missing_artifact_count: 13
invalid_artifact_count: 0
status: needs_baselines
```

The remaining missing artifacts are non-local:

| App/path | Remaining missing baselines |
| --- | --- |
| `graph_analytics / graph_visibility_edges_gate` | `optix_visibility_anyhit`, `optix_native_graph_ray_bfs`, `optix_native_graph_ray_triangle_count` |
| `road_hazard_screening / road_hazard_native_summary_gate` | `postgis_when_available` |
| `segment_polygon_hitcount / segment_polygon_hitcount_native_experimental` | `postgis_when_available` |
| `segment_polygon_anyhit_rows / segment_polygon_anyhit_rows_prepared_bounded_gate` | `optix_prepared_bounded_pair_rows`, `postgis_when_available_for_same_pair_semantics` |
| `polygon_pair_overlap_area_rows / polygon_pair_overlap_optix_native_assisted_phase_gate` | `postgis_when_available_for_same_unit_cell_contract` |
| `polygon_set_jaccard / polygon_set_jaccard_optix_native_assisted_phase_gate` | `postgis_when_available_for_same_unit_cell_contract` |

Goal971 remains conservative:

```text
strict same-semantics baseline-complete rows: 7
active-gate limited rows: 4
baseline-pending rows: 6
public speedup claims authorized: 0
```

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal974_remaining_local_baselines_test \
  tests.goal973_deferred_decision_baselines_test \
  tests.goal971_post_goal969_baseline_speedup_review_package_test \
  tests.goal846_active_rtx_claim_gate_test

OK
```

## Verdict

`ACCEPT` from Codex.

All locally available baseline evidence has been collected for the remaining
six rows. The rest requires suitable external services or hosts: PostGIS and
OptiX-capable RTX execution. No public speedup claim is authorized.
