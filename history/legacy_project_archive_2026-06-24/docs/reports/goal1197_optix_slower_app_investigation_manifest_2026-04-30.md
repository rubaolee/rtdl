# Goal1197 OptiX Slower-App Investigation Manifest

Date: 2026-04-30

Goal1197 is an investigation manifest for OptiX-slower app paths. It does not authorize public wording changes, release, or speedup claims.

## Summary

- valid: `True`
- slower app count: `4`
- control app count: `1`
- same-scale repair app count: `1`
- pod ready after review: `True`

## Pod Policy

Run this as one batched pod session only after review. Do not restart a pod per app. Preserve all artifacts, logs, and failed JSON files; copy them back before interpreting results.

## Slower App Investigation Rows

| App | Observed ratio | Hypothesis | Scales | Decision rule |
| --- | ---: | --- | --- | --- |
| `database_analytics` | `0.791844` | OptiX traversal is real, but compact-summary timing may be dominated by Python/ctypes packing, candidate bitset transfer, or grouping continuation overhead. | `[{"copies": 30000, "iterations": 10}, {"copies": 100000, "iterations": 10}, {"copies": 300000, "iterations": 5}]` | If OptiX remains slower at 100k and 300k on warm-query phase, classify current DB compact-summary OptiX as interface/continuation limited and keep positive wording blocked. |
| `graph_analytics` | `0.500014` | The OptiX visibility any-hit path may be doing more launch/setup work than the Embree summary path, or the graph edge mapping is too sparse/branchy to amortize GPU traversal overhead. | `[{"copies": 30000}, {"copies": 60000}, {"copies": 120000}]` | If OptiX remains about 2x slower while phase fields are comparable, classify graph visibility as current-implementation GPU-overhead dominated and do not promote positive wording. |
| `polygon_pair_overlap_area_rows` | `0.839019` | Native-assisted candidate discovery may be correct but not enough to beat Embree because exact continuation and chunk handling dominate. | `[{"chunk_copies": 100, "copies": 10000}, {"chunk_copies": 100, "copies": 20000}, {"chunk_copies": 100, "copies": 40000}]` | If OptiX only loses by a small margin while chunk_copies is held constant, inspect chunk overhead and candidate count parity before deciding whether native batching can plausibly flip the result. |
| `polygon_set_jaccard` | `0.54876` | The Jaccard path has both performance loss and observed chunk-sensitive/nondeterministic parity behavior; stability must be proven before any future positive wording. | `[{"chunk_copies": 1, "copies": 8192}, {"chunk_copies": 8, "copies": 8192}, {"chunk_copies": 64, "copies": 8192}, {"chunk_copies": 512, "copies": 8192}]` | If any chunk configuration fails parity, keep Jaccard blocked and file a correctness/stability task before more performance tuning. |

## Commands

### database_analytics

- `db_embree_scale_sweep`

  `python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario sales_risk --copies {copies} --iterations {iterations} --output-mode compact_summary --strict --output-json docs/reports/goal1197_optix_slower_app_investigation/{label}_{copies}.json`

- `db_optix_scale_sweep`

  `python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies {copies} --iterations {iterations} --output-mode compact_summary --strict --output-json docs/reports/goal1197_optix_slower_app_investigation/{label}_{copies}.json`

### graph_analytics

- `graph_embree_visibility_sweep`

  `python3 examples/rtdl_graph_analytics_app.py --backend embree --scenario visibility_edges --copies {copies} --output-mode summary > docs/reports/goal1197_optix_slower_app_investigation/{label}_{copies}.json`

- `graph_optix_visibility_sweep`

  `python3 scripts/goal889_graph_visibility_optix_gate.py --copies {copies} --output-mode summary --validation-mode analytic_summary --chunk-copies 0 --strict --output-json docs/reports/goal1197_optix_slower_app_investigation/{label}_{copies}.json`

### polygon_pair_overlap_area_rows

- `polygon_pair_embree_sweep`

  `python3 examples/rtdl_polygon_pair_overlap_area_rows.py --backend embree --copies {copies} --output-mode summary > docs/reports/goal1197_optix_slower_app_investigation/{label}_{copies}.json`

- `polygon_pair_optix_sweep`

  `python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app pair_overlap --mode optix --copies {copies} --output-mode summary --validation-mode analytic_summary --chunk-copies {chunk_copies} --output-json docs/reports/goal1197_optix_slower_app_investigation/{label}_{copies}.json`

### polygon_set_jaccard

- `polygon_jaccard_embree_reference`

  `python3 examples/rtdl_polygon_set_jaccard.py --backend embree --copies {copies} --output-mode summary > docs/reports/goal1197_optix_slower_app_investigation/{label}_{copies}_{chunk_copies}.json`

- `polygon_jaccard_optix_chunk_stability`

  `python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies {copies} --output-mode summary --validation-mode analytic_summary --chunk-copies {chunk_copies} --output-json docs/reports/goal1197_optix_slower_app_investigation/{label}_{copies}_{chunk_copies}.json`

## Positive Controls

- `road_hazard_screening`: `positive_control`, observed ratio `4.014155`. Should remain faster if the pod and measurement setup are sane.

## Same-Scale Repair Targets

- `hausdorff_distance`: `same_scale_repair`. Goal1195 final bundle used Embree copies=2000 and OptiX copies=1200000, so the raw 13.7x ratio is not a valid same-scale speedup. Collect same-scale or explicitly normalized Hausdorff Embree/OptiX evidence before any positive public ratio wording.

## Boundary

Goal1197 is an investigation manifest for OptiX-slower app paths. It does not authorize public wording changes, release, or speedup claims.

