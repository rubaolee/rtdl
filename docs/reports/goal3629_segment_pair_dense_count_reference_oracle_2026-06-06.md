# Goal3629 - Segment-Pair Dense Count Reference Oracle

Date: 2026-06-06

Status: internal same-contract oracle foundation. This does not authorize release, public speedup wording, RTDL-beats-RayJoin wording, RayJoin paper reproduction, broad RT-core speedup, true zero-copy, automatic partner selection, or app-specific native engine logic.

## Purpose

Goal3625 made the segment-pair predicate contract executable. Goal3627 made the typed output residency target concrete. Goal3629 adds the missing local oracle for future backend conformance:

`segment_pair_left_id_dense_counts_reference(left_segments, right_segments)`

This function computes dense counts by left segment index using the strict-v0 predicate from Goal3625.

## Contract

For each left segment and each right segment:

1. Evaluate `segment_pair_intersection_strict_v0`.
2. Increment the left-index count only when `decision.hit` is true.
3. Count denominator-degenerate, collinear, near-parallel, non-finite, or other ambiguous exclusions in `ambiguous_pair_count`.
4. Count outside-parametric-bounds misses in `rejected_pair_count`.

The output object records:

- `group_capacity`;
- `counts`;
- `hit_pair_count`;
- `ambiguous_pair_count`;
- `rejected_pair_count`;
- `decision_reasons`;
- false release/public-speedup flags.

## Why It Matters

Future CuPy, OptiX fast-count, and OptiX host-refined conformance should compare to a single same-contract oracle. Without this, each benchmark script can accidentally define a slightly different "LSI count" contract.

This is deliberately not a performance path. It is a correctness oracle for contract tests and future pod validation.

## Boundary

This oracle is Python reference logic. It does not prove backend conformance, does not prove device-resident execution, does not prove true zero-copy, and does not authorize public claims.
