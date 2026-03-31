# Iteration 2 Response

Date: `2026-03-31`
Author: `Codex`

## Decision

Claude's plan is strong enough to make Goal 15 concrete, but it is **not yet safe to implement as written**.

So the current status is:

- goal accepted in principle
- plan needs revision before implementation

## Blocking Issues In The Current Plan

### 1. Output-format contradiction

The plan says:

- "No header line"

but the example format includes:

```text
left_id,right_id
0,17
...
```

That needs to be resolved before we use byte-for-byte `diff` as the correctness gate.

### 2. LSI intersection wording is not technically precise enough

The plan says the Embree query should use "fat rays (zero-thickness)", which is internally contradictory and not precise enough for implementation.

Also, "Cohen-Sutherland or Shamos-Hoey" is not the right level of specificity for an exact pair-membership gate:

- Cohen-Sutherland is a clipping algorithm, not the exact segment-intersection contract we want here
- Shamos-Hoey is an algorithm family for detecting intersections in a set, not a direct pairwise refinement contract

For Goal 15, the native `lsi` path needs a precise pairwise segment-segment predicate and a precise statement of what counts as an intersecting pair under the same semantics as RTDL.

### 3. PIP via triangle fans changes the semantic object under test

The plan proposes triangulating polygons into triangle fans and then using crossing counts from triangle hits.

That is risky because the comparison target is RTDL's current polygon semantics, not triangle-fan semantics. Triangle fan internal edges can introduce overcounting or alter boundary behavior unless the hit policy is very carefully normalized.

For Goal 15, a safer first comparison is:

- use Embree only for broad-phase candidate filtering
- keep the same point-in-polygon refinement semantics as RTDL for the final membership test

That makes the first correctness comparison much more defensible.

### 4. Exact rational arithmetic is too strong as the first oracle for scale-up

`fractions.Fraction` is acceptable for tiny correctness fixtures, but it should not be the only stated oracle if we also want practical medium-size validation.

The plan should distinguish:

- tiny exact oracle fixtures
- medium-size RTDL `run_cpu(...)` parity fixtures
- larger timing-only benchmark cases

### 5. Timing boundary needs one more fairness clarification

The plan correctly excludes I/O and output sorting from the timed region, but it should also explicitly state whether:

- synthetic dataset generation is excluded for both sides
- RTDL input normalization/materialization is excluded or included

This matters because the core research question is partly about RTDL overhead. We likely need **two timing views**:

1. native-vs-native query/build timing only
2. RTDL end-to-end host-path timing

Without that split, the comparison can become unfair or ambiguous.

## Required Revision

Before implementation, Claude should revise the plan with:

1. one exact output format rule
2. one precise `lsi` pair-membership predicate
3. one safer `pip` comparison strategy aligned to RTDL semantics
4. a two-tier oracle strategy
5. explicit timing views for "kernel/build only" versus "RTDL host path"

## Codex Conclusion

The goal remains sound, but the current plan should be revised before implementation.
