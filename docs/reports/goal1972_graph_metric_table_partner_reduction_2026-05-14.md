# Goal1972 Graph Metric-Table Partner Reduction

Date: 2026-05-14

Status: implementation slice with pod timing

## Why This Goal Exists

After Goal1969, the remaining known weak spot in the control-app lane was
`graph_analytics`: it was extremely fast, but for the wrong reason. The v2
control path used a tiny RawKernel that wrote closed-form formulas from
`copies`, so the timing measured launch overhead more than a reusable partner
continuation primitive.

Goal1972 replaces that graph closed-form kernel with a generic metric/value
table reduction. This keeps the native RTDL engine app-agnostic and makes the
v2 graph control row use reusable partner algebra instead of app-specific
formula injection.

## Implemented Slice

`src/rtdsl/partner_adapters.py` now exposes:

```text
partner_metric_table_reduce_by_key(metric_keys, values, output_metric_keys,
                                   partner="torch"|"cupy",
                                   reduce="sum"|"max"|"min")
```

The helper maps arbitrary metric IDs to requested output metric IDs with
sort/searchsorted, then delegates to the existing partner group reduction
primitives. It is intentionally generic: the keys are opaque integer metric
IDs, and the values are ordinary partner tensors.

`examples/rtdl_control_apps_cupy_rawkernel.py` now builds metric rows for the
authored graph control case and reduces them with:

- `sum` for edge/vertex/triangle/visibility counts
- `max` for BFS level depth

The public graph summary remains identical to the v1.8 oracle, but the path is
no longer a one-off RawKernel that writes `2 * copies`, `3 * copies`, and so on.

## Boundary

This does not add graph semantics to the native engine. It also does not yet
prove a general graph traversal acceleration claim: the input rows for this
control example are still authored in Python, and pod timing is still required.

The design lesson is narrower and useful for v2.0: graph-like apps need generic
partner-owned metric tables and reductions, not app-specific native
continuations and not closed-form timing shortcuts.

## Pod Timing

The RTX 2000 Ada pod rerun used `copies=1000`, `partner=cupy`, and the
Goal1972 metric-table path:

| App | Copies | v1.8 median s | v2 median s | v2/v1.8 | Correct |
| --- | ---: | ---: | ---: | ---: | --- |
| `graph_analytics` | 1000 | 18.060916 | 0.000054 | 0.000003x | yes |

This is no longer the previous closed-form RawKernel, but the claim remains
bounded: the authored input rows are small, and this does not prove arbitrary
graph traversal acceleration.

Artifact:

- `docs/reports/goal1972_pod_graph_metric_table_control_perf.json`

## Validation

Local focused validation:

```text
PYTHONPATH=src;. py -3 -m unittest tests.goal1972_graph_metric_table_partner_reduction_test
```

Pod timing was collected on the RTX 2000 Ada pod.
