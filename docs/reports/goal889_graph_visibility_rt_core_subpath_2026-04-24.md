# Goal889 Graph Visibility RT-Core Sub-Path

Date: 2026-04-24

## Result

Goal889 adds a bounded RT-core candidate to the unified graph app:

```text
graph_analytics / visibility_edges
```

The original Goal889 scenario mapped graph candidate edges through RTDL
visibility rows. Goal913 later corrected the copied-graph cloud shape by
moving graph candidate edges to explicit pair semantics:
`rt.visibility_pair_rows(...)`. In OptiX mode, the corrected path dispatches
ray/triangle any-hit traversal for exactly the caller-provided graph edges
instead of expanding copied observers and copied targets as a Cartesian matrix.

This gives the graph app a real graph-to-RT sub-path without falsely claiming
that existing BFS or triangle-count CSR paths use RT cores.

## New Gate

The new strict gate is:

```bash
scripts/goal889_graph_visibility_optix_gate.py
```

It compares CPU Python reference visibility-edge output with OptiX any-hit
visibility-edge output. On local macOS without OptiX, non-strict mode records
backend unavailability instead of treating it as a correctness failure.

## Matrix And Manifest

`graph_analytics` now records:

- performance class: `optix_traversal`
- readiness: `needs_real_rtx_artifact`
- maturity: `rt_core_partial_ready`

The RTX manifest now includes deferred entry:

```text
graph_analytics / graph_visibility_edges_gate
```

The deferred batch now has:

- active entries: `5`
- deferred entries: `12`
- baseline contracts: `17`

## Boundary

This is only graph visibility-edge filtering. It is not:

- BFS acceleration,
- triangle-count acceleration,
- shortest-path acceleration,
- graph database acceleration,
- general graph analytics acceleration.

## Verification

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal889_graph_visibility_optix_gate_test \
  tests.goal814_graph_optix_rt_core_honesty_gate_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal822_rtx_cloud_manifest_claim_boundary_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal886_rtx_cloud_start_packet_test
```

Result: `48 tests OK`.

Pre-cloud gate:

```bash
PYTHONPATH=src:. python3 scripts/goal824_pre_cloud_rtx_readiness_gate.py \
  --output-json docs/reports/goal889_pre_cloud_readiness_after_graph_visibility_2026-04-24.json
```

Result: `valid: true`.
