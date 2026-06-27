# Goal3324 - Closed-Shape Topology-Aware Membership Candidate Primitive

Date: 2026-06-04

## Purpose

Goals3320-3322 showed that RTDL's fast prepared point / closed-shape count route is useful but not broad enough for county-style CDB topology. The route is exact on checked simple-chain domains, but it overcounts the county start256 slice by 12 rows across 7 point IDs.

Goal3324 records the next reusable primitive candidate in the primitive hierarchy:

```text
candidate.closed_shape_topology_membership_count_2d
```

This is a candidate contract only. It is not an executable native path and does not authorize any performance or release claim.

## Problem Statement

The current fast route answers:

```text
How many generic point/closed-shape membership events did this device-side predicate emit?
```

For CDB-style workloads, the app often needs a stricter question:

```text
For this point and this topology-aware closed shape, which face/ring/chain owns the boundary decision, and how should duplicate boundary events be counted?
```

The difference matters. Goal3322 found a structured county overcount:

- exact total: 1417;
- fast total: 1429;
- delta: +12;
- mismatch points: 7;
- positive deltas: 7;
- negative deltas: 0;
- several mismatching points have duplicate coordinates.

## Candidate Contract

Inputs:

- caller point columns with stable caller IDs;
- closed-shape geometry;
- optional face/ring/chain topology columns;
- explicit boundary ownership policy;
- explicit duplicate policy;
- capacity and overflow policy.

Outputs:

- membership count or grouped count keyed by caller point ID;
- ownership status or policy status;
- topology policy metadata;
- overflow/fallback status.

Required semantics:

- deterministic boundary ownership;
- deterministic duplicate handling;
- exactness policy recorded in metadata;
- fail-closed fallback when topology metadata is absent or insufficient;
- no app/entity naming in native symbols.

## Duplicate-Gate Position

The primitive deliberately overlaps existing closed-shape and count capabilities, so it records alternatives:

- `traversal.count_hits`;
- `rows.point_closed_shape_boundary_event_columns`;
- `reduction.grouped`;
- `candidate.device_grouped_candidate_merge`.

It is distinct because:

- `traversal.count_hits` does not own topology/boundary ownership;
- `rows.point_closed_shape_boundary_event_columns` emits witnesses but does not classify membership;
- `reduction.grouped` aggregates keys but does not define closed-shape topology semantics;
- `candidate.device_grouped_candidate_merge` merges candidate streams but does not own boundary degeneracy policy.

## App-Agnostic Boundary

This candidate must stay generic. The engine may see topology columns and policy names, but it must not see:

- RayJoin-specific map/entity semantics;
- CDB source filenames as native behavior;
- paper-system reproduction policy;
- application assignment interpretation.

RayJoin, GIS, or benchmark-specific interpretation stays in Python app code.

## Claim Boundary

- `release_authorized`: false
- `public_speedup_claim_authorized`: false
- `rt_core_speedup_claim_authorized`: false
- `true_zero_copy_claim_authorized`: false
- `rtdl_beats_rayjoin_claim_authorized`: false
- `rayjoin_paper_reproduction_claim_authorized`: false

