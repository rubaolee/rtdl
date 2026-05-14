# Goal1991 Metric-Table Payload Batch for Graph Analytics

Date: 2026-05-14

Status: implementation slice

## Why This Goal Exists

Goal1972 removed the original graph control-row shortcut: the v2 path no longer
uses a tiny app-local RawKernel that writes closed-form values from `copies`.
It uses generic metric-table reductions instead.

Goal1991 tightens that design one more step. The graph example now uses a
metric-table payload handoff and a batched metric-table reduction API, so the
example is written as reusable partner algebra rather than two ad hoc
`cp.asarray(...)` plus reduction calls.

## What Changed

The partner adapter now exposes:

```text
metric_table_payload_to_partner_columns(...)
partner_metric_table_reduce_batch(...)
```

`metric_table_payload_to_partner_columns` accepts caller-supplied metric-key,
value, and output-key arrays and converts them into partner-owned columns.

`partner_metric_table_reduce_batch` accepts multiple named metric-table
reduction specs and returns named partner outputs. The individual reductions
still use the existing generic `partner_metric_table_reduce_by_key` primitive;
the new API is the public shape that graph-like continuations can reuse without
inventing app-local glue for every summary.

## Boundary

This does not add graph traversal semantics to the native engine. It is not a
new BFS, triangle-count, visibility, or graph database primitive. It is generic
metric-table payload handoff plus partner reduction.

The existing Goal1972 pod timing remains the performance evidence for this row.
Goal1991 is a structure cleanup that makes the graph continuation contract more
reusable and easier to teach. It is not a broad graph acceleration claim, not an
RT-core claim, and not a final v2.0 release claim.
