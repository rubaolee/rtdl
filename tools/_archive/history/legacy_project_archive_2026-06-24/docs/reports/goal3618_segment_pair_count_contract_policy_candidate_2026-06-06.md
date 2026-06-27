# Goal3618 - Segment-Pair Count Contract Policy Candidate

Date: 2026-06-06

Status: internal v2.9 primitive-contract policy candidate. This does not authorize release, public speedup wording, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, true zero-copy, or native default-route claims.

## Purpose

Goal3614 accepted the Goal3612/Goal3613 RayJoin LSI repair with boundary and identified one important remaining risk: the project needs a documented primitive contract for segment-pair counting before public claims.

Goal3618 records the current candidate contract for internal benchmark use. It is deliberately conservative: it documents what is currently measured and what remains unresolved.

## Primitive

Generic primitive family:

- `segment_pair_intersection_count`
- `segment_pair_left_id_dense_count`
- `segment_pair_intersection_rows`

These are generic geometry primitives. They must not contain RayJoin, CDB, GIS, county, parcel, or paper-specific ownership semantics.

## Current Internal Benchmark Contract

For current RayJoin public-CDB same-contract benchmark rows, a segment-pair hit is counted when all of the following hold:

1. The two finite 2D segments are non-degenerate enough for the active predicate to divide by the cross-product denominator.
2. The denominator check uses a threshold equivalent to the current benchmark predicate:
   - CuPy dense baseline: `fabs(denom) < 1.0e-7` rejects the pair.
   - repaired OptiX left-id dense count: `dabsf(denom) < 1.0e-7f` rejects the pair in the strict device predicate.
3. The parametric intersection values satisfy endpoint-inclusive bounds:
   - `0.0 <= t <= 1.0`
   - `0.0 <= u <= 1.0`
4. Collinear overlap is not counted by the current benchmark predicate. Near-parallel and collinear cases rejected by the denominator policy are outside this current count contract.

## What Goal3613 Proved

Goal3613 proved that the repaired OptiX left-id dense count route matches the CuPy dense baseline on the measured public-CDB slices:

| Slice | CuPy LSI Count | OptiX Dense Count | Diff Count |
| --- | ---: | ---: | ---: |
| `start=256`, `count=4096` | 4977 | 4977 | 0 |
| `start=0`, `count=4096` | 5612 | 5612 | 0 |

It did not prove that all future geometries, all adversarial collinear cases, or all host-refined routes are equivalent.

## Important Boundary: Float Strict vs Host Double Refine

There are two useful routes:

- fast device-resident count: strict float-side any-hit predicate;
- host-refined exact count: OptiX candidates plus host-side double refinement.

They are not automatically identical for every possible geometry. Current evidence says both can match the CuPy benchmark contract on tested public-CDB slices. A public primitive contract must decide one of:

- float strict predicate is the published count contract;
- host double refinement is the published count contract;
- both are separate named contracts;
- fast path is allowed only when ambiguity telemetry says no fallback is needed.

Until that decision is made and tested, public claims should stay bounded.

## Required Future Work Before Public Claim

Before any public RayJoin or generic segment-pair count claim:

1. Add adversarial fixtures for near-parallel, endpoint-touching, tiny-segment, zero-length, and collinear-overlap cases.
2. Decide whether collinear overlap belongs in the primitive contract.
3. Decide whether denominator threshold is absolute, scale-aware, or user-configurable.
4. Decide whether the fast device path must expose ambiguity telemetry and fall back to host/double or higher-precision handling.
5. Add cross-route conformance tests covering CuPy, OptiX fast device count, and OptiX host-refined count.

## Current Route Guidance

For internal v2.9 public-CDB RayJoin benchmark rows:

- use repaired OptiX left-id dense count for LSI when the benchmark contract is the current non-collinear endpoint-inclusive count;
- use exact prepared OptiX host-refined count when richer row evidence or conservative fallback is needed;
- do not use either route for public claims until the above contract is formalized and externally reviewed.

## Boundary

This is a policy candidate and internal benchmark guardrail. It is not a public API specification and not a release packet.
