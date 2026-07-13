# Goal5023: Full Overlay Distinct Query-Batch Route

Date: 2026-07-05

## Purpose

Goal5022 proved prepared LSI base reuse on distinct LSI query batches, but only
for the LSI phase.  Goal5023 extends that to the full writer-free binary overlay
route:

- split the left top4 County input into distinct chain-contiguous query batches;
- keep one prepared right/base Zipcode LSI session;
- run the full overlay body for each batch: LSI, reprojection, sort, PIP,
  midpoint PIP, carrier, and descriptor consumer.

This is the first full-overlay query-batch measurement in this line.  It is not
the paper text route and not a cold CLI one-shot result.

## Implementation

Added app-layer query batching to
`Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`:

- `--query-chain-batches N`
- `_slice_dataset_by_chain_range(...)`
- `_split_dataset_by_chain_batches(...)`

The slice builder creates a complete `DatasetArrays` batch, not just sliced LSI
segments.  It rebuilds:

- chain offsets and point counts;
- point arrays and point ids;
- segment ids and segment arrays;
- directed CDB face segments;
- packed LSI segments;
- packed directed point-location segments;
- packed query points.

The route remains app-layer.  No RTDL core/native primitive was added.

## Regime

The reported result is:

- top4 County x Zipcode representative input;
- writer-free binary overlay route;
- warm long-lived process;
- prepared LSI base/right session;
- distinct chain-contiguous left query batches;
- full overlay body for each batch;
- no paper-text writer;
- no author comparison;
- no cold CLI one-shot headline.

## Validation

Local:

```text
PYTHONPATH=src py -3 -m py_compile \
  Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py

PYTHONPATH=src py -3 -m unittest \
  tests.goal5021_prepared_lsi_base_session_test

Ran 6 tests in 0.002s
OK
```

POD:

```text
python -m unittest tests.goal5021_prepared_lsi_base_session_test

Ran 6 tests in 0.001s
OK
```

POD artifact:

- `history/internal_docs/rtdl_goal5023_full_overlay_distinct_chain_batches_top4.json`

## Result

### Batch Rows

| Batch | Chains | Edges | LSI rows | Descriptor pairs | writer-free | LSI | Downstream |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 537 | 563,220 | 149,350 | 7,190 | 3.835s | 1.618s | 2.216s |
| 1 | 537 | 569,647 | 134,254 | 7,592 | 0.767s | 0.056s | 0.710s |
| 2 | 538 | 572,160 | 144,718 | 4,438 | 0.783s | 0.055s | 0.729s |

### Important Aggregates

```text
first batch writer-free:        3.835s
later batch writer-free median: 0.775s
all-batch median:               0.783s
all-batch average:              ~1.795s
```

The all-batch median is useful but not sufficient by itself; the first batch and
later batches must be reported separately because the first batch pays the
initial grouped-range/scaled-cache cost.

### Why It Moved

Batch 0:

```text
grouped_range_ensure: 0.981s
scaled_cache_ensure:  0.635s
LSI total:            1.618s
```

Batches 1 and 2:

```text
grouped_range_ensure: ~0.000001s
scaled_cache_ensure:  ~0.055s / ~0.048s
LSI total:            ~0.056s / ~0.055s
```

The full overlay route confirms the LSI-only Goal5022 finding: in a prepared
base/session, grouped-range work amortizes across distinct same-domain query
batches.  Later full-overlay batches are dominated by downstream PIP/sort/carrier
work, not LSI.

## What This Proves

- Prepared-base query-many is a real full-overlay route, not just an LSI probe.
- The app can run distinct chain-contiguous query batches through the full
  writer-free binary overlay body.
- Later query batches run at about `0.77-0.78s` on this top4 representative.
- RTDL remains a generic system; RayJoin batching and descriptor semantics stay
  in the app.

## What This Does Not Prove

This does not prove:

- cold CLI speedup;
- paper text route speedup;
- author parity;
- 10x across all regimes;
- arbitrary external query workload behavior;
- full device-resident carrier payoff.

The first batch remains expensive.  A product claim must state whether the use
case is first-query, later-query, or amortized multi-query.

## Current Honest State

This is the strongest performance result in the v2.14.3 line:

- canonical warm-process fast-pack route: `~4.22s`;
- generic LSI prewarm route: `2.386s` median;
- prepared LSI base full-overlay single full query: `1.031s` median;
- prepared LSI base full-overlay distinct query batches:
  - first batch `3.835s`;
  - later batches `~0.77-0.78s`;
  - all-batch average `~1.795s`.

The remaining hard work is now clearly downstream:

- vertex PIP on the right/base points is about `0.31-0.37s` per batch;
- reprojection/sort is about `0.30s`;
- carrier/consumer is about `0.07s` for later batches;
- first-batch grouped-range/scaled-cache still costs about `1.6s`.

## Exit Label

```text
completed_full_overlay_distinct_query_batches__prepared_base_later_batches_under_0_8s__first_batch_cost_still_visible
```
