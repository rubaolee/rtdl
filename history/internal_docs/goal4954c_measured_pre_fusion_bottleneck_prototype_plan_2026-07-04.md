# Goal4954-C Measured Pre-Fusion Bottleneck Prototype Plan

Date: 2026-07-04

Status: proposed_pending_review

Parent:

- `history/internal_docs/goal4954b_writer_free_binary_baseline_measurement_2026-07-04.md`
- Antigravity verdict: `approve_goal4954b_writer_free_measurement_close_open_goal4954c`

## Purpose

Goal4954-C prototypes pre-fusion improvements against the measured writer-free
binary baseline.

Goal4954-B measured the median writer-free hot path:

```text
writer-free hot path: 5.309487 s
vs AuthorOfficial overlay compute: 126.12x slower
```

Measured median bottlenecks:

| Phase | Median seconds |
|---|---:|
| binary grouped row construction | 1.748347 |
| LSI rows | 1.213490 |
| sort total | 0.836403 |
| reprojection | 0.741140 |
| descriptor-pair consumer | 0.688320 |

Therefore, Goal4954-C must not blindly optimize only reprojection/sort. The
first prototype targets the largest measured pre-fusion component:

```text
binary grouped row construction + downstream descriptor consumer
```

## Owner Invariant

RTDL is a generic spatial dataflow system. RayJoin is an app.

Goal4954-C may create app-owned prototype code under internal/reproduction
artifacts. It may not change RTDL core/runtime unless a later reviewed
non-RayJoin proof promotes a generic mechanism.

## Prototype C1: Grouped Columnar Carrier

Goal4954-B used a flat point-row representation:

```text
group_id, item_order, x, y, label_a, label_b, alt_label,
source_side_id, source_element_id, keep
```

This repeats group-level labels for every point row, producing:

```text
64,459 groups
673,371 point rows
```

Goal4954-C C1 will test a grouped columnar carrier:

### Group-level columns

- `group_offset`
- `group_length`
- `label_a`
- `label_b`
- `alt_label`
- `source_side_id`
- `source_element_id`

### Point-level columns

- `x`
- `y`

This is still generic. It is a grouped-row columnar representation and does not
encode RayJoin paper text or output-chain byte format.

## Downstream Consumer

The same logical consumer is preserved:

```text
descriptor_pair_count
```

But it consumes group-level labels and `group_length` instead of repeated
point-level labels.

Two aggregate variants are allowed:

- `group_count_by_descriptor_pair`
- `point_count_by_descriptor_pair`

The second should match the old consumer's total row-count semantics without
physically repeating labels per point.

## Variables Held Constant

To isolate the effect of the grouped carrier, Goal4954-C C1 must not change:

- LSI route;
- reprojection implementation;
- sort implementation;
- vertex PIP route;
- midpoint generation;
- midpoint PIP route;
- AuthorOfficial comparator;
- input data;
- OptiX SDK/native build.

## Forbidden

Goal4954-C does not authorize:

- RTDL core/runtime edits;
- public API exposure;
- Layer 4 fusion;
- raw OptiX callbacks;
- traversal-side Numba/PTX injection;
- RayJoin-specific hidden core kernel;
- claiming competitiveness with AuthorOfficial if the measured gap remains
  large.

## Measurement

Run on the same POD/environment as Goal4954-B:

```text
POD: root@213.173.108.15:14399
GPU: NVIDIA RTX 4000 Ada Generation
OptiX SDK: NVIDIA/optix-sdk v9.0.0
RTDL HEAD: 8cc0597b
Input: public County x Soil sample
```

Collect at least 3 runs.

Report:

- old Goal4954-B median;
- C1 grouped-carrier median;
- delta for binary row construction;
- delta for descriptor-pair consumer;
- total writer-free hot path delta;
- whether correctness/context invariants still hold.

## Success / Failure

`grouped_carrier_win_continue`

- binary construction and consumer cost materially decrease;
- no correctness boundary is weakened;
- no RTDL core pollution occurs.

`grouped_carrier_correct_but_not_faster_stop`

- output shape and consumer work correctly;
- performance does not improve enough to justify expanding this path.

`grouped_carrier_wrong_reject`

- group counts or aggregate semantics are inconsistent;
- app-specific semantics leak into the generic carrier;
- measurement is invalid.

## Recommended Next After C1

If C1 wins, Goal4954-D should decide whether to:

- keep it app-owned as a RayJoin paper-reproduction improvement;
- or attempt non-RayJoin proof before promoting a generic grouped carrier.

If C1 does not win, the next pre-fusion prototype should move to reprojection
and sort only if the measured phase table still justifies it.
