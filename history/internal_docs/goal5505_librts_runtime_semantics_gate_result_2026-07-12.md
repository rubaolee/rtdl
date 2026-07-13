# Goal5505: LibRTS Runtime Semantics Gate

## Status

`implemented__same_input_pod_boundary_gate__review_pending`

## Setup

One float32 box and five deterministic query boxes were passed, one query at
a time, to both implementations on the same POD:

```text
POD       NVIDIA RTX 4000 Ada Generation / driver 570.133.07
author    RTSpatial query -query_type range-intersects -index_type rtspatial
          -load_factor 1
RTDL      prepare_aabb_index_2d_columns + prepared.count(range_intersects)
```

The geometry SHA-256 is
`2256d450210f56d7032284e87fae70b46ed1686a441f1bf4fad9ed8fba544ba2` and the
query SHA-256 is
`d427b5164a23be371779550b0b368b2fd8a4e2f08b449765ccdc74ef46002b95`.

## Result

```text
case order                         author  RTDL  CPU inclusive  source model
interior overlap                       1      1       1             1
edge touch                             1      1       1             1
corner touch                           1      1       1             1
one-ULP overlap before box max         1      1       1             1
one-ULP gap after box max              1      0       0             1
total                                  5      4       4             5
```

The source-driven model matches all five author runtime observations. RTDL
differs from the author on one synthetic case: `one_ulp_gap_after_box_max`.
The committed WKT order is recorded in the machine-readable result. The CPU
inclusive oracle is not the author truth on this widened float32 interval.
This is exactly why Goal5502's CPU oracle cannot settle the full-input
disagreements by itself.

## Interpretation

This is a real same-input POD runtime diagnostic, not a full-input resolution.
It validates the missing forward/backward source interpretation and localizes
one reproducible author-vs-RTDL behavior difference, but it does not prove that
the two large official-archive count disagreements have the same cause. It
also does not establish a paper-level boundary policy or relation equality.

No RTDL core change is authorized by this goal. A generic fix would require a
broader independent contract and a regression matrix that demonstrates the
desired behavior is generic, not a LibRTS-specific compatibility patch.

## Claim Boundary

```json
{
  "author_gpu_runtime_executed": true,
  "same_input_runtime_fixture_agreement": true,
  "author_validity_proven_for_full_inputs": false,
  "full_input_adjudication": false,
  "rtdl_core_change_authorized": false,
  "author_specific_rtdl_core_behavior_authorized": false,
  "performance_ratio_authorized": false,
  "paper_reproduction_claimed": false,
  "embree_in_scope": false
}
```

Machine-readable evidence:

`Paper-reproduction-apps/librts-paper/results/goal5505_runtime_semantics_gate.json`
