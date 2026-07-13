# Goal4954-E Pre-Fusion Decision

Date: 2026-07-04

Status: completed_pending_review

Parent:

- Goal4954-A: binary contract and measurement plan
- Goal4954-B: writer-free baseline measurement
- Goal4954-C: grouped carrier prototype
- Goal4954-D: non-RayJoin grouped-carrier proof and reprojection/sort plan

Exit label requested:

`pre_fusion_layers_deliver_product_value_but_author_class_performance_deferred_to_layer4`

## Purpose

Goal4954-E closes the pre-fusion program authorized by the owner:

> Do all practical Layer 1/2/3 binary overlay operator work before Layer 4
> traversal-side fusion.

Layer 4 remains out of scope:

- no raw callbacks;
- no traversal-side Numba/PTX injection;
- no in-traversal fusion compiler;
- no hidden RayJoin kernel in RTDL core.

## Summary Of What Was Done

### Goal4954-A: Contract

Defined a generic binary overlay/event contract:

- grouped carrier;
- descriptor labels;
- group offsets/lengths;
- point columns;
- downstream descriptor-pair consumer.

Hard invariant:

> RTDL is generic. RayJoin is an app.

Antigravity verdict:

`approve_goal4954a_contract_measurement_plan_open_goal4954b`

### Goal4954-B: Writer-Free Baseline

Built and ran the writer-free binary baseline on POD:

```text
POD: root@213.173.108.15:14399
GPU: NVIDIA RTX 4000 Ada Generation
OptiX SDK: NVIDIA/optix-sdk v9.0.0
RTDL OptiX lib: /root/rtdl_goal4954/build/librtdl_optix.so
```

Median result:

```text
writer-free hot path: 5.309487s
ratio vs AuthorOfficial overlay compute: 126.12x slower
```

Antigravity verdict:

`approve_goal4954b_writer_free_measurement_close_open_goal4954c`

### Goal4954-C: Grouped Carrier Prototype

Changed app-owned binary representation from repeated point rows to grouped
columnar carrier.

Median result:

```text
writer-free hot path: 3.835318s
ratio vs AuthorOfficial overlay compute: 91.10x slower
speedup vs Goal4954-B: 1.384x
```

Grouped carrier + consumer improvement:

```text
2.436667s -> 1.021675s
2.385x faster
```

Antigravity verdict:

`approve_goal4954c_grouped_carrier_win_continue`

### Goal4954-D: Non-RayJoin Proof

Created a synthetic non-RayJoin grouped-carrier proof:

```text
rayjoin_imported: false
cdb_required: false
authorofficial_required: false
paper_text_required: false
pass: true
```

This proves the grouped carrier is a generic spatial/dataflow representation
candidate, not inherently RayJoin-specific.

Antigravity verdict:

`approve_goal4954d_non_rayjoin_grouped_carrier_proven`

### Goal4954-E Numeric Binary Route

Measured Option B from Goal4954-D:

- paper sink keeps exact rational route for byte-for-byte correctness;
- binary operator route uses numeric coordinates for database-style downstream
  consumers.

This is not a paper-output route and does not claim byte equality.

Median result:

```text
writer-free hot path: 2.921366s
ratio vs AuthorOfficial overlay compute: 69.39x slower
speedup vs Goal4954-B: 1.818x
speedup vs Goal4954-C: 1.313x
```

## Performance Table

| Route | Median hot path | Ratio vs AuthorOfficial overlay compute | Meaning |
|---|---:|---:|---|
| 4954-B flat binary rows | 5.309487s | 126.12x slower | Writer removed, repeated labels still expensive. |
| 4954-C grouped carrier | 3.835318s | 91.10x slower | Generic grouped representation helps substantially. |
| 4954-E numeric binary route | 2.921366s | 69.39x slower | Numeric binary route helps more, but still far from author. |

## Median Phase Table: Final Numeric Binary Route

| Phase | Median seconds |
|---|---:|
| LSI rows | 1.196542 |
| numeric reprojection | 0.221340 |
| numeric sort total | 0.444451 |
| grouped carrier construction | 0.909884 |
| grouped descriptor consumer | 0.059860 |
| total writer-free hot path | 2.921366 |

Compared with exact grouped route:

| Phase | Exact grouped route | Numeric binary route | Change |
|---|---:|---:|---:|
| reprojection | 0.736632s | 0.221340s | -0.515292s |
| sort total | 0.842339s | 0.444451s | -0.397888s |
| total hot path | 3.835318s | 2.921366s | -0.913953s |

## What This Proves

1. The paper text writer was not the only issue.
2. Binary operator framing was correct because it separated correctness sink
   from operator performance.
3. Grouped columnar carrier is a real pre-fusion improvement.
4. The grouped carrier is not inherently RayJoin-specific.
5. Numeric binary route is faster than exact paper-compatible reprojection/sort.
6. Layer 1/2/3 work can deliver meaningful product value without Layer 4.

## What This Does Not Prove

This does not prove RTDL is competitive with the author's fused C++/CUDA/OptiX
overlay compute.

Even after the best pre-fusion route measured here:

```text
2.921366s / 0.0421s = 69.39x slower
```

The remaining gap is too large to explain away as paper writer overhead.

## Remaining Bottlenecks

Final numeric route still has:

| Remaining phase | Median seconds |
|---|---:|
| LSI rows | 1.196542 |
| grouped carrier construction | 0.909884 |
| numeric sort total | 0.444451 |
| numeric reprojection | 0.221340 |

The two biggest remaining costs are:

1. LSI row production/materialization;
2. app-owned grouped carrier construction.

These are still pre-fusion costs, but their scale relative to the author's
`0.0421s` overlay compute shows that author-class performance likely requires
Layer 4-style traversal fusion or native compiled end-to-end overlay logic.

## Product Decision

Goal4954 should close with:

`pre_fusion_layers_deliver_product_value_but_author_class_performance_deferred_to_layer4`

Meaning:

- pre-fusion Layer 1/2/3 work is valuable;
- binary operator framing is correct;
- grouped carrier should continue toward productization only with the
  non-RayJoin proof/generic API gates;
- numeric binary route is a legitimate product-performance line distinct from
  the paper exact sink;
- but author-class overlay performance remains out of reach without a later
  Layer 4 decision.

## Recommended Next Project

Do not continue ad hoc micro-optimizing the RayJoin paper app.

The next project should be a reviewed productization goal:

```text
Generic grouped carrier + descriptor-pair consumer productization
```

with:

- source placement review;
- non-RayJoin tests in the normal test suite;
- no RayJoin/CDB/AuthorOfficial dependency in RTDL core;
- optional RayJoin app adapter using the generic carrier;
- no public performance claim beyond the measured public sample.

Separately, if the owner wants author-class performance, open a distinct Layer 4
R&D goal with explicit authorization. Do not smuggle it into Goal4954.

## Files And Artifacts

Primary artifacts:

- `history/internal_docs/goal4954b_artifacts/writer_free_binary_summary_run1.json`
- `history/internal_docs/goal4954b_artifacts/writer_free_binary_summary_run2.json`
- `history/internal_docs/goal4954b_artifacts/writer_free_binary_summary_run3.json`
- `history/internal_docs/goal4954c_artifacts/grouped_carrier_summary_run1.json`
- `history/internal_docs/goal4954c_artifacts/grouped_carrier_summary_run2.json`
- `history/internal_docs/goal4954c_artifacts/grouped_carrier_summary_run3.json`
- `history/internal_docs/goal4954e_artifacts/numeric_binary_summary_run1.json`
- `history/internal_docs/goal4954e_artifacts/numeric_binary_summary_run2.json`
- `history/internal_docs/goal4954e_artifacts/numeric_binary_summary_run3.json`

Internal scripts:

- `history/internal_docs/goal4954b_writer_free_binary_overlay_measure.py`
- `history/internal_docs/goal4954c_grouped_carrier_measure.py`
- `history/internal_docs/goal4954d_non_rayjoin_grouped_carrier_proof.py`
- `history/internal_docs/goal4954e_numeric_binary_route_measure.py`

Review records:

- `history/internal_docs/antigravity_review_goal4954_binary_overlay_operator_pre_fusion_program_2026-07-04.md`
- `history/internal_docs/antigravity_review_goal4954a_binary_overlay_contract_and_measurement_plan_2026-07-04.md`
- `history/internal_docs/antigravity_review_goal4954b_writer_free_binary_baseline_measurement_2026-07-04.md`
- `history/internal_docs/antigravity_review_goal4954c_grouped_carrier_prototype_results_2026-07-04.md`
- `history/internal_docs/antigravity_review_goal4954d_non_rayjoin_grouped_carrier_proof_and_reprojection_sort_plan_2026-07-04.md`

## Final Boundary

Goal4954 did not change RTDL core/runtime.

Goal4954 did not expose a public API.

Goal4954 did not do Layer 4 fusion.

Goal4954 did not claim author-class performance.

Goal4954 did produce a measured, genericity-checked pre-fusion path from:

```text
5.309s writer-free hot path
to
2.921s numeric binary hot path
```

That is a meaningful pre-fusion product direction, not a final high-performance
RayJoin victory.
