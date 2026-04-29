# Goal1129 Graph Phase Split Local Audit

Date: 2026-04-29

This goal adds observable phase timing to graph app payloads before any further
cloud work. It does not promote graph public RTX wording and does not authorize
whole-graph speedup claims.

## Change

- `examples/rtdl_graph_bfs.py` now reports fixture construction,
  query/materialization, and native summary postprocess timing.
- `examples/rtdl_graph_triangle_count.py` now reports the same phase split.
- `examples/rtdl_graph_analytics_app.py` now reports visibility-edge timing
  split and aggregate `graph_phase_totals_sec` for the unified app.
- The existing honesty boundary remains: only `visibility_edges` is the current
  OptiX RT-core claim candidate; BFS and triangle-count remain gated for public
  RTX wording.

## Local Artifacts

Commands:

`PYTHONPATH=src:. python3 examples/rtdl_graph_analytics_app.py --backend cpu_python_reference --scenario all --copies 1000 --output-mode summary`

`PYTHONPATH=src:. python3 examples/rtdl_graph_analytics_app.py --backend embree --scenario all --copies 1000 --output-mode summary`

Artifacts:

- `docs/reports/goal1129_graph_local_phase_split_cpu_2026-04-29.json`
- `docs/reports/goal1129_graph_local_phase_split_embree_2026-04-29.json`

## Phase Totals

| Backend | Copies | Input sec | Query/materialize sec | Visibility rows sec | Native summary sec |
| --- | ---: | ---: | ---: | ---: | ---: |
| `cpu_python_reference` | `1000` | `0.004581791930831969` | `0.004834165913052857` | `7.9149645830038935` | `0.014042875962331891` |
| `embree` | `1000` | `0.0046821251744404435` | `0.023205957957543433` | `0.00844783300999552` | `0.007835874916054308` |

## Interpretation

The phase split confirms the key local bottleneck: CPU visibility-pair rows
dominate at this scale, while Embree ray traversal removes that bottleneck. For
NVIDIA RTX work, the next cloud run must capture the equivalent OptiX
visibility_edges phase separately from BFS/triangle row materialization and
native summary continuation.

## Verification

Focused graph suite:

`PYTHONPATH=src:. python3 -m unittest tests.goal1129_graph_phase_split_contract_test tests.goal889_graph_visibility_optix_gate_test tests.goal949_graph_native_summary_continuation_test tests.goal738_graph_app_scaled_summary_test -v`

Result: 20 tests OK.

## Boundary

Graph public wording remains `public_wording_not_reviewed`. This audit improves
diagnostic separation only.
