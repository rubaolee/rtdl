# Goal1965 Partner Column Compaction Primitives

Date: 2026-05-14

Status: implementation slice

## Why This Goal Exists

Goal1958 called out row materialization as a remaining v2.0 weakness. Count and
flag apps can stay compact, but row-output apps still need a reusable way to
filter and page partner-owned columns without returning to Python lists.

## Implemented Slice

`src/rtdsl/partner_adapters.py` now exposes:

```text
partner_mask_indices(mask, partner=...)
partner_take_columns_by_indices(columns, indices, partner=...)
partner_compact_columns_by_mask(columns, mask, partner=...)
```

These functions operate on generic column tables. Torch uses `torch.nonzero`;
CuPy uses `cupy.nonzero`; both keep the selected rows in partner-owned tensors.

## Design Boundary

This does not add app rows to native code. The native engine still emits generic
identity/payload columns. Partner compaction decides which generic rows survive,
and application code assigns meaning to those compacted rows.

The intended pattern is:

```text
generic columns + partner mask -> compact generic columns -> app view
```

## What This Enables Next

This is the basis for:

- device-resident row paging for arbitrary witness/candidate rows;
- filtering false positives before host serialization;
- shared post-processing for row-output apps such as segment/shape any-hit;
- reducing the gap between count-like v2 speedups and row-output v2 speedups.

## What Remains

This is a column utility, not a final paging API. We still need bounded page
contracts, stable row ordering rules, and pod-scale timing evidence before
claiming that arbitrary row-output apps are broadly accelerated.

