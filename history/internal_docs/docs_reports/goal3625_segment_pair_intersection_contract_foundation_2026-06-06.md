# Goal3625 - Segment-Pair Intersection Contract Foundation

Date: 2026-06-06

Status: internal next-version primitive-contract foundation. This does not authorize release, public speedup wording, RTDL-beats-RayJoin wording, RayJoin paper reproduction, broad RT-core speedup, true zero-copy, automatic partner selection, or app-specific native engine logic.

## Purpose

Goal3618 recorded a policy candidate for segment-pair counting after the RayJoin LSI repair. Goal3625 turns that policy into executable, app-agnostic contract metadata:

- a Python reference contract in `src/rtdsl/segment_pair_contracts.py`;
- a discoverable candidate primitive node in `src/rtdsl/primitive_hierarchy.py`;
- a regenerated primitive catalog entry in `docs/rtdl_primitive_catalog.md`;
- adversarial fixture validation for the first seven required geometry categories.

This is still a candidate contract. It is not a public API specification.

## Candidate Primitive

Candidate primitive node:

`rows.segment_pair_intersection_rows_2d`

Discovery aliases include:

- `segment_pair_intersection`
- `segment_pair_intersection_count`
- `segment_pair_left_id_dense_count`
- `line_segment_intersection`
- `finite_segment_intersection`
- `lsi_count`

The node is intentionally generic. It owns finite 2-D segment-pair intersection semantics only. Join interpretation, map/entity lookup, paper-system meaning, and caller-specific grouping remain app or partner code.

## Executable Contract

The executable contract is:

`segment_pair_intersection_strict_v0(left, right)`

Candidate version:

`rtdl.segment_pair_contract.v0.candidate`

Current v0 semantics:

1. Inputs are two finite 2-D segments.
2. Non-finite coordinates are rejected and marked ambiguous.
3. Denominator policy is absolute: `abs(denom) < 1.0e-7` rejects the pair.
4. Rejected denominator-degenerate pairs are marked ambiguous.
5. Endpoint-inclusive parametric bounds are used: `0.0 <= t <= 1.0` and `0.0 <= u <= 1.0`.
6. Collinear overlap is not counted by this v0 fast-count contract.
7. Successful hits expose `t`, `u`, and the intersection point.

This matches the current internal RayJoin same-contract fast-count predicate family: the CuPy dense baseline and the repaired OptiX left-id dense count path use the non-collinear endpoint-inclusive absolute-denominator contract.

## Adversarial Fixture Set

The initial fixture set covers:

| Case | Category | Expected hit | Expected ambiguous | Meaning |
| --- | --- | ---: | ---: | --- |
| `proper_crossing` | proper | true | false | Interior crossing is counted. |
| `endpoint_touch` | endpoint | true | false | Endpoint-inclusive contract counts the hit. |
| `outside_bounds_same_lines` | outside | false | false | Infinite lines cross outside finite segment intervals. |
| `parallel_disjoint` | parallel | false | true | Parallel pairs are outside the v0 fast contract. |
| `collinear_overlap` | collinear | false | true | Collinear overlap is excluded and flagged ambiguous. |
| `near_parallel_below_abs_epsilon` | near_parallel | false | true | Near-parallel denominator below `1.0e-7` is excluded. |
| `tiny_degenerate_left` | degenerate | false | true | Zero-length segment is excluded through denominator degeneracy. |

Validation summary:

```text
valid: true
case_count: 7
categories: collinear, degenerate, endpoint, near_parallel, outside, parallel, proper
```

## Why This Matters

The RayJoin LSI repair showed that raw performance is not enough; the primitive also needs a published contract before public wording. This foundation gives the next version a concrete path:

1. keep the fast OptiX count path for measured internal slices;
2. define the generic contract independent of RayJoin;
3. test adversarial cases before any public primitive claim;
4. decide whether fast float count, host double refinement, or both become separate named contracts.

## What Remains

Before public contract promotion:

1. Add backend conformance tests for CPU reference, CuPy dense, OptiX fast device count, and OptiX host-refined count.
2. Add larger adversarial sweeps around the denominator threshold.
3. Decide whether collinear overlap remains excluded or becomes a separate contract.
4. Decide whether the denominator threshold should stay absolute, become scale-aware, or become caller-configurable.
5. Add ambiguity telemetry to fast paths if fallback is required for excluded cases.
6. Seek the pending Claude review for the broader Goal3619/3622 next-version direction and get final 3-AI consensus before treating this as roadmap-final.

## Boundary

Goal3625 is a contract foundation only. It is not release evidence, not a public API specification, not RayJoin paper reproduction, not RTDL-beats-RayJoin evidence, and not public speedup wording.
