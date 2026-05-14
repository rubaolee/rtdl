# Goal1962 Partner Unique-Pair Group Counts

Date: 2026-05-14

Status: implementation slice

## Why This Goal Exists

Goal1960 landed the first shared partner reduction primitives, but the segment
/ shape hit-count path still carried a private helper named
`count_unique_pairs_by_ids`. That helper was not native-engine app
customization, but it was still the wrong shape for v2.0: a serious RTDL
program should be able to reuse generic identity-table reductions instead of
rewriting one-off pair de-duplication code in each app adapter.

## Implemented Slice

`src/rtdsl/partner_adapters.py` now exposes:

```text
partner_group_count_unique_pairs_by_key(group_keys, item_keys, output_group_keys, partner=...)
```

The primitive counts unique `(group_key, item_key)` pairs for each requested
output group key. It supports PyTorch and CuPy tensors, runs without host row
materialization, and preserves arbitrary output group IDs rather than assuming
that IDs are dense or zero-based.

The segment / shape hit-count adapters now route their generic witness rows
through this shared primitive. The old private runtime hook remains only as a
fake-runtime compatibility fallback for existing local tests.

## Design Boundary

This is not an app-specific native reduction and does not put segment, polygon,
or hit-count semantics into the RTDL engine. There is no app-specific native reduction
in this slice. The native side still emits generic witness identity columns.
The partner layer performs a generic unique-pair grouped count over those
columns, and app adapters interpret the result.

In short:

```text
generic witness rows -> partner unique-pair grouped count -> app result
```

## What This Solves

This is a reusable building block for:

- segment / shape hit counts;
- candidate-pair duplicate removal;
- identity-preserving set cardinality;
- future app continuations that need per-group unique item counts.

## What It Does Not Solve Yet

This primitive does not by itself finish the richer continuation algebra still
needed for full v2.0 breadth:

- reusable graph traversal and triangle-count summaries;
- exact polygon overlay and area accumulation;
- ranked KNN top-k output;
- exact Hausdorff max-distance reductions;
- DBSCAN cluster expansion;
- Barnes-Hut force-vector accumulation.

Those requirements need additional generic partner primitives, not new
app-customized native engine code.
