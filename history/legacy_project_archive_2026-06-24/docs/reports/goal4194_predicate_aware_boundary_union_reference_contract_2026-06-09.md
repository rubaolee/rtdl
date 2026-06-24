# Goal4194: Predicate-Aware Boundary Union Reference Contract

Date: 2026-06-09

## Purpose

Goal4193 registered `continuation.predicate_aware_boundary_union` as a
candidate primitive after the RT-DBSCAN counts-only probe showed that the next
real win is not another app-specific shortcut. Goal4194 adds the partner-free
Python reference contract for that candidate.

This is still a reference contract. It does not promote the primitive, change
route selection, add native code, or authorize release/performance wording.

## Contract

The helper `predicate_aware_boundary_union_reference(...)` consumes:

- `point_count`;
- fixed-radius candidate pairs;
- caller-owned boolean predicate flags;
- a deterministic boundary-assignment policy.

The first policy is `lowest_component_root`. Predicate-true candidate pairs
form components. Predicate-false boundary items can attach to neighboring
predicate-true components. If more than one neighboring component is possible,
the reference assigns the boundary item to the lowest component root.

The output is a compact, deterministic summary:

- component labels;
- component sizes;
- true/false pair accounting;
- boundary candidate counts;
- assignment policy metadata;
- explicit flags saying that app logic is not native-engine logic and route
  promotion is not authorized.

## Why Lowest-Root Matters

The lowest-root policy avoids rank-based union roots so that candidate-pair
ordering does not change the semantic signature. That makes this usable as a
same-contract oracle before any native or partner implementation exists.

## Boundary

This helper does not encode DBSCAN, clustering, epsilon/min-points, or any
domain-specific policy. The caller owns predicate meaning. RTDL owns only
generic boolean predicate flags, fixed-radius candidate pairs, component roots,
boundary items, and deterministic assignment metadata.

Goal4194 does not authorize release, public speedup claims, broad RT-core
claims, true-zero-copy claims, automatic partner selection, route promotion, or
app-specific native engine logic.

## Next Step

The implementation lane can now compare future native/partner candidates
against this reference contract. Promotion still requires same-contract pod
evidence, dense/sparse profiles, route-decision review, and external consensus.
