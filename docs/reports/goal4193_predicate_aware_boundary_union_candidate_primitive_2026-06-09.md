# Goal4193: Predicate-Aware Boundary Union Candidate Primitive

Date: 2026-06-09

## Purpose

Goal4190 showed that the lightweight counts-only mixed-predicate shortcut is not
enough for a major RT-DBSCAN-style performance win. Counts-only signatures match
the grouped-stream reference, but policy-bound component-size signatures do not,
and the single-pass direct-status path reaches only a modest `1.056x` at 4M
points.

Goal4193 records the real next primitive target in the RTDL primitive hierarchy:

`continuation.predicate_aware_boundary_union`

This is intentionally marked `candidate_behavior`, not stable or promoted.

## Contract Shape

The candidate is generic:

- caller-supplied vertex predicate flags;
- fixed-radius candidate pairs;
- component roots;
- boundary items;
- deterministic boundary-assignment policy metadata;
- policy-aware component/count signatures.

It must not encode DBSCAN, clustering, epsilon/min-points, or any app policy in
native ABI names or engine behavior.

## Why It Exists

The existing `continuation.fixed_radius_graph` primitive is not enough for this
case because it does not own caller-supplied predicate flags or boundary-item
assignment. The existing grouped reductions are not enough because they do not
perform fixed-radius component grouping. Segmented row paging is also not enough
because paging rows does not resolve deterministic boundary assignment.

## Acceptance Bar Before Promotion

Before this candidate can become a promoted route, it needs:

- same-contract parity against current grouped-stream component signatures when
  component-size distribution is part of the contract;
- counts-only parity when border tie-breaks are explicitly outside the contract;
- deterministic boundary-assignment metadata;
- dense and sparse RTX pod profiles;
- external review;
- no app-specific native symbols or hidden automatic route selection.

## Boundary

This goal does not implement the primitive and does not authorize release,
public speedup wording, broad RT-core wording, whole-app claims, true-zero-copy
claims, route promotion, automatic partner selection, or app-specific native
engine logic.

It gives the implementation lane a precise generic target so future work does
not keep bouncing between RT-DBSCAN app-specific tricks and unreviewed route
promotion.
